from odoo import models, fields, api, _


class AccountInvoiceReport(models.Model):
    _inherit ='account.invoice.report'

    product_categ_id = fields.Many2one('product.category', string='Product Brand  ', readonly=True)

