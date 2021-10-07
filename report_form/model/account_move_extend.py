from odoo import models,fields,api,_


class AccountMove(models.Model):
    _inherit ='account.move'

    so_date = fields.Datetime(string='SO Date', compute='_get_so_date')

    @api.depends('invoice_origin')
    def _get_so_date(self):
        for rec in self:
            if rec.invoice_origin is not None:
                rec.so_date = self.env['sale.order'].search(
                    [('name', '=', rec.invoice_origin)]).date_order

