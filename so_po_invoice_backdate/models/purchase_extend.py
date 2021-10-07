from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.constrains('date_order')
    def check_date_order(self):

        for order in self:

            order_date = datetime.strptime(order.date_order.strftime('%Y-%m-%d'), '%Y-%m-%d').date()

            if not order_date:
                continue

            today = fields.Date.today()
            user = self.env.user
            po_allow_back_date = user.po_allow_back_date
            po_allow_current_date = user.po_allow_current_date
            po_allow_future_date = user.po_allow_future_date
            po_back_days = user.po_back_days or 0
            backdate_limit = today - relativedelta(days=po_back_days)

            if order_date > today and not po_allow_future_date:
                raise UserError(_('You are not allowed to do future date transaction.'))

            elif order_date == today and not po_allow_current_date:
                raise UserError(_('You are not allowed to do current date transaction.'))

            elif order_date < today and (not po_allow_back_date or order_date < backdate_limit):
                raise UserError(_('You are not allowed to do backdate transaction or your backdate is beyond limit.'))
