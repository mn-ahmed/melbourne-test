from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class BillLanding(models.Model):
    _name = 'bill.landing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Bill Landing'

    def _get_line_numbers(self):
        line_num = 1
        for line_rec in self:
            line_rec.line_no = line_num
            line_num += 1

    @api.model
    def _default_get_currency(self):
        currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        return currency_id


    name = fields.Char(string='BL Number', copy=False, index=True, required=True, tracking=True)
    line_no = fields.Integer(compute='_get_line_numbers', string='No', readonly=False, default=False)
    partner_id = fields.Many2one('res.partner', string='Vendor Name', domain=[('supplier', '=', True)], required=True, tracking=True)
    feet_20 = fields.Char('No.20 Ft', tracking=True)
    feet_40 = fields.Char('No.40 Ft', tracking=True)
    bill = fields.Selection([('yes', 'Yes'), ('no', 'NO')], string='BL', default='yes', tracking=True)
    co = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='CO', default='no', tracking=True)
    pl_cl = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='PL & CI', default='yes', tracking=True)
    form_ed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='FORM E/D', default='no', tracking=True)
    etd_date = fields.Date('ETD', tracking=True)
    eta_date = fields.Date('ETA', tracking=True)
    date_clear = fields.Date('Cleared Date', tracking=True)
    brand_id = fields.Many2one('product.brand', string='Brand')
    description = fields.Text('Description')
    custom_duty = fields.Float('Custom Duty', tracking=True)
    commerial_tax = fields.Float('Commerial Tax', tracking=True)
    advanced_Tax = fields.Float('Advanced Tax', tracking=True)
    other_charges = fields.Float('Other Charges', tracking=True)
    po_amount = fields.Float(compute='_get_po_amount', string='PO amount', store=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    invoice_number = fields.Char('Invoice Number',  tracking=True)
    bill_number = fields.Many2one('account.move', string='Vendor Bill Number', tracking=True)
    inv_currency_id = fields.Many2one('res.currency', string='Inv Currency', related='bill_number.currency_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_get_currency)
    invoice_amount = fields.Float('Actual Invoice Amount', tracking=True)
    sparepart_invoice = fields.Char('Spare Parts Invoice', tracking=True)
    declare_inv_amount = fields.Char('Declare Invoice Amount', tracking=True)
    freight_charges = fields.Char('Freight Charges', tracking=True)
    insurance = fields.Char('Insurance', tracking=True)
    certificate_number = fields.Char('Cretificate Number', tracking=True)
    hs_code = fields.Char('Apply HS Code Charges', tracking=True)
    po_charges = fields.Char('PO Charges', tracking=True)
    agent_fees = fields.Char('Agent Fees', tracking=True)
    rk_paid = fields.Char('RK Paid Unofficially', tracking=True)
    transporation = fields.Char('Transporation', tracking=True)
    warehouse_charges = fields.Char('Warehouse Unloading Charges', tracking=True)
    sd_fields = fields.Char('SD', tracking=True)
    license_fees = fields.Char('License Fees', tracking=True)
    user_id = fields.Many2one('res.users', string='Bill Representative', default=lambda self: self.env.user)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'You can not have two B/L Number with the same name !')
    ]

    @api.depends('custom_duty', 'commerial_tax', 'advanced_Tax', 'other_charges')
    def _get_po_amount(self):
        self.po_amount = self.custom_duty + self.commerial_tax + self.advanced_Tax + self.other_charges

    @api.onchange('bill_number')
    def onchange_bill_number(self):
        if self.bill_number:
            self.invoice_amount = self.bill_number.amount_total

    def button_confirm(self):
        self.write({'state': 'pending'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_done(self):
        self.write({'state': 'done'})

    def unlink(self):
        for bl in self:
            if not bl.state == 'cancel':
                raise UserError(_('In BL to delete a bill of landing, you must cancel it first.'))
        return super(BillLanding, self).unlink()



