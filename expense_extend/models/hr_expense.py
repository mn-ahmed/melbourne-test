from odoo import api, fields, models, _

class HrExpense(models.Model):

    _inherit = "hr.expense"

    @api.model
    def _default_department_id(self):
        return self.env.user.employee_id.department_id

    department_id = fields.Many2one('hr.department', string='Department', default=_default_department_id,
                                    states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                            'refused': [('readonly', False)]},)
    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id, index=True,
                                states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                        'refused': [('readonly', False)]},)

    state = fields.Selection(selection_add=[('first_approved', 'First Approved'),('approved',)])

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == 'draft':
                expense.state = "draft"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            elif expense.sheet_id.state == "first_approved":
                expense.state = "first_approved"
            elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
                expense.state = "approved"
            elif not expense.sheet_id.account_move_id:
                expense.state = "reported"
            else:
                expense.state = "done"

    @api.onchange('employee_id')
    def onchange_employee_department(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id, index=True,
                                states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                        'refused': [('readonly', False)]}, )

    state = fields.Selection(selection_add=[('first_approved', 'First Approved'),('approve',)])

    sequence = fields.Char("Sequence", default="New",copy=False)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}

    def action_submit_sheet(self):
        self.write({'state': 'submit'})
        self.activity_update()
        if self.sequence == 'New':
            self.sequence = self.env['ir.sequence'].next_by_code('hr.expense.sheet') or _('New')

    def first_approve_expense_sheets(self):
        self.write({'state': 'first_approved'})

    @api.constrains('expense_line_ids', 'employee_id')
    def _check_employee(self):
        for sheet in self:
            employee_ids = sheet.expense_line_ids.mapped('employee_id')
            if len(employee_ids) > 1 or (len(employee_ids) == 1 and employee_ids != sheet.employee_id):
                # raise ValidationError(_('You cannot add expenses of another employee.'))
                print("You cannot add expenses of another employee.")