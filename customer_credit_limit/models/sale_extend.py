from odoo import api, fields, models, exceptions, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_limit = fields.Float('Credit Limit Amount', related='partner_id.credit_limit')
    over_credit = fields.Boolean('Unallow Credit Limit', related='partner_id.over_credit')
    total_due = fields.Monetary('Total Due Amount', related='partner_id.amount_due', currency_field='company_currency_id')
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')
    sale_date = fields.Date('Date', required=True, readonly=False, default=fields.date.today())
    invoice_date_due = fields.Date('Invoice Due Date', readonly=True, copy=False, compute='_get_date_due')

    @api.depends('partner_id')
    def _get_date_due(self):
        self.invoice_date_due = ''
        if self.partner_id and (self.over_credit is True):
            query = """ SELECT a.invoice_date_due as date FROM account_move a
                        WHERE a.partner_id is not null
                        AND a.partner_id='""" + str(self.partner_id.id) + """' AND invoice_payment_state='not_paid';"""
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
            for val in result:
                self.invoice_date_due = val['date']

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if not self.env['res.users'].has_group('customer_credit_limit.group_allow_credit_limit'):
            if self.total_due and (self.over_credit is True) and (self.credit_limit < self.amount_total+self.total_due):
                raise exceptions.ValidationError(
                    _('Sorry you can not confirm sale order! This customer credit amount is more than limit.  Please contact to your manager.')
                )

            if self.invoice_date_due:
                if (self.invoice_date_due <= self.sale_date):
                    raise exceptions.ValidationError(
                        _('Sorry you can not confirm sale order! This customer credit due date is over. Please contact to your manager.')
                    )
        return res
