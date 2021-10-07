from odoo import models, fields, api, _
from odoo.exceptions import UserError

class account_payment(models.Model):
    _inherit = "account.payment"

    def post(self):
        res = super(account_payment, self).post()
        for rec in self:
            branch = rec.branch_id
            if rec.partner_type == 'customer':
                if rec.payment_type == 'inbound':
                    sequence_code = branch.cus_sequence_id
                    rec.name = sequence_code._next()
                if rec.payment_type == 'outbound':
                    sequence_code = branch.cusout_sequence_id
                    rec.name = sequence_code._next()
            if rec.partner_type == 'supplier':
                if rec.payment_type == 'inbound':
                    sequence_code = branch.venout_sequence_id
                    rec.name = sequence_code._next()
                if rec.payment_type == 'outbound':
                    sequence_code = branch.ven_sequence_id
                    rec.name = sequence_code._next()
        return res