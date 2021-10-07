from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_extend(self):
        if self.partner_id:
            self.sale_by = self.partner_id.sales_man_id.id
            self.branch_id = self.partner_id.branch_id.id