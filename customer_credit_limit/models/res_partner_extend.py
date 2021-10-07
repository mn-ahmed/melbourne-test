from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = "res.partner"

    credit_limit = fields.Float('Credit Limit Amount')
    over_credit = fields.Boolean(string="Unallow Over Credit?")
    amount_due = fields.Monetary('Due Amount', compute='_compute_amount_due')

    @api.depends('credit', 'debit')
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.credit - rec.debit
