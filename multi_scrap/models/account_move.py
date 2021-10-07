from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', store=True)


