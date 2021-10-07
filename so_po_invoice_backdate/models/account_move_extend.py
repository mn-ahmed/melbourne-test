from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.constrains('invoice_date')
    def check_date_order(self):

        for account_move in self:

            invoice_date = account_move.invoice_date

            if not invoice_date:
                continue

            today = fields.Date.today()
            user = self.env.user
            invoice_allow_back_date = user.invoice_allow_back_date
            invoice_allow_current_date = user.invoice_allow_current_date
            invoice_allow_future_date = user.invoice_allow_future_date
            invoice_back_days = user.invoice_back_days or 0
            backdate_limit = today - relativedelta(days=invoice_back_days)

            if invoice_date > today and not invoice_allow_future_date:
                raise UserError(_('You are not allowed to do future date transaction.'))

            elif invoice_date == today and not invoice_allow_current_date:
                raise UserError(_('You are not allowed to do current date transaction.'))

            elif invoice_date < today and (not invoice_allow_back_date or invoice_date < backdate_limit):
                raise UserError(_('You are not allowed to do backdate transaction or your backdate is beyond limit.'))
