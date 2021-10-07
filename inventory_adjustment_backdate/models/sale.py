from odoo import fields, models, api,_
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    backdate = fields.Datetime(string='Back Date', readonly=True,
                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},default=fields.Datetime.now)

    @api.onchange('backdate')
    def onchange_backdate(self):
        if self.backdate:
            self.date_order = self.backdate

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': self.backdate,
        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

