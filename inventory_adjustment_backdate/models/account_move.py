from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Date(required=False, states={'posted': [('readonly', True)]}, index=True, readonly=False)