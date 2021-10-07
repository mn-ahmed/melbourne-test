from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_paid_amount = fields.Char(string='Payment Amount', compute='_get_total_')

    payment_date = fields.Date(string='Payment Date', compute='_get_payment_date')

    # znl 16 sept 2020
    partner_city = fields.Char(related="partner_id.city", string='Partner City',store=True)
    partner_state_id = fields.Many2one('res.country.state', related="partner_id.state_id", string='Partner State ',store=True)
    partner_township_id = fields.Many2one('res.township', related="partner_id.township_id", string='Partner Township ',store=True)

    @api.depends('total_paid_amount')
    def _get_payment_date(self):
        for rec in self:
            if rec.total_paid_amount:
                rec.payment_date = self.env['account.payment'].search([('communication', '=', rec.name)],
                                                                      limit=1).payment_date

    @api.depends('amount_total_signed', 'amount_residual_signed')
    def _get_total_(self):
        for rec in self:
            total_amount = rec.amount_total- rec.amount_residual_signed
            rec.total_paid_amount = format(total_amount, ".2f") + ' K'
            # total_amount= rec.amount_total - rec.amount_residual
            # rec.total_paid_amount = format(total_amount, ".2f") + ' K'
