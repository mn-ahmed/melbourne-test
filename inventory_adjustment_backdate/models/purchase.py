from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('date_order')
    def _onchange_date(self):
        if self.date_order:
            self.date_planned = self.date_order

    def button_approve(self, force=False):
        result = super(PurchaseOrder, self).button_approve(force=force)
        self.write({'state': 'purchase', 'date_approve': self.date_order})
        return result