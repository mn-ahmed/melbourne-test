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
    date = fields.Date('BL Date', required=True, tracking=True, default=fields.date.today())
    bill_number = fields.Many2one('account.move', string='Vendor Bill Number', tracking=True)
    inv_currency_id = fields.Many2one('res.currency', string='Inv Currency', related='bill_number.currency_id', store=True)
    invoice_amount = fields.Float('Actual Invoice Amount', tracking=True)
    sparepart_invoice = fields.Char('Spare Parts Invoice', tracking=True)
    declare_inv_amount = fields.Char('Declare Invoice Amount', tracking=True)
    freight_currency_id = fields.Many2one('res.currency', string='Freight Currency', default=_default_get_currency)
    freight_rate = fields.Float(digits=(0, 12), default=1.0, string='Freight Rate', related='freight_currency_id.rate',
                                help='The rate of the currency to the currency of rate 1')
    freight_price_unit = fields.Float('Freight Cost', digits='Product Price', required=True)
    freight_charges = fields.Monetary(currency_field="freight_currency_id", string='Freight Charges', store=True, copy=True)
    insurance_currency_id = fields.Many2one('res.currency', string='Insurance Currency', default=_default_get_currency)
    insurance_rate = fields.Float(digits=(0, 12), default=1.0, string='Insurance Rate', related='insurance_currency_id.rate',
                                  help='The rate of the currency to the currency of rate 1')
    insurance_price_unit = fields.Float('Insurance Cost', digits='Product Price', required=True)
    insurance = fields.Monetary(currency_field="insurance_currency_id", string='Insurance Charges', store=True, copy=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, index=True, default=lambda self: self.env.company)
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
        ('name_uniq', 'UNIQUE (name)', 'You can not have two B/L Number with the same name !'),
        ('date_check', "CHECK ( (etd_date <= eta_date))", "The ETD date must be anterior to the ETA date.")
    ]

    @api.depends('custom_duty', 'commerial_tax', 'advanced_Tax', 'other_charges')
    def _get_po_amount(self):
        self.po_amount = self.custom_duty + self.commerial_tax + self.advanced_Tax + self.other_charges

    @api.onchange('freight_charges')
    def _onchange_freight_currency(self):
        for rec in self:
            if rec.freight_charges:
                date = rec.date
                company = rec.company_id
                company_currency = rec.company_id.currency_id
                if rec.freight_currency_id != company_currency:
                    rec.freight_price_unit = rec.freight_currency_id._convert(rec.freight_charges,
                                                                      company_currency,
                                                                      company, date)
                else:
                    rec.freight_price_unit = rec.freight_charges

    @api.onchange("insurance")
    def _onchange_insurance_currency(self):
        for rec in self:
            if rec.insurance:
                date = rec.date
                company = rec.company_id
                company_currency = rec.company_id.currency_id
                if rec.insurance_currency_id != company_currency:
                    rec.insurance_price_unit = rec.insurance_currency_id._convert(rec.insurance,
                                                                        company_currency,
                                                                        company, date)
                else:
                    rec.insurance_price_unit = rec.insurance


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



