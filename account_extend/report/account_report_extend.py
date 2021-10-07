from odoo import tools
from odoo import models, fields, api

from functools import lru_cache


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    # znl 16 sept 2020
    city_id = fields.Many2one('res.city', string=' City')
    state_id = fields.Many2one('res.country.state', string='State ')
    township_id = fields.Many2one('res.township', string='Township ')

    _depends = {
        'account.move': [
            'name', 'state', 'type', 'partner_id', 'invoice_user_id', 'fiscal_position_id',
            'invoice_date', 'invoice_date_due', 'invoice_payment_term_id', 'invoice_partner_bank_id',
        ],
        'account.move.line': [
            'quantity', 'price_subtotal', 'amount_residual', 'balance', 'amount_currency',
            'move_id', 'product_id', 'product_uom_id', 'account_id', 'analytic_account_id',
            'journal_id', 'company_id', 'currency_id', 'partner_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'uom.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id','x_city_id','state_id','township_id'],
    }

    @api.model
    def _select(self):
        return '''
                SELECT
                    line.id,
                    line.move_id,
                    line.product_id,
                    line.account_id,
                    line.analytic_account_id,
                    line.journal_id,
                    line.company_id,
                    line.company_currency_id                                    AS currency_id,
                    line.partner_id AS commercial_partner_id,
                    move.name,
                    move.state,
                    move.type,
                    move.partner_id,
                    move.invoice_user_id,
                    move.fiscal_position_id,
                    move.invoice_payment_state,
                    move.invoice_date,
                    move.invoice_date_due,
                    move.invoice_payment_term_id,
                    move.invoice_partner_bank_id,
                    partner.x_city_id as city_id,
                    partner.state_id as state_id,
                    partner.township_id as township_id,
                    -line.balance * (move.amount_residual_signed / NULLIF(move.amount_total_signed, 0.0)) * (line.price_total / NULLIF(line.price_subtotal, 0.0))
                                                                                AS residual,
                    -line.balance * (line.price_total / NULLIF(line.price_subtotal, 0.0))    AS amount_total,
                    uom_template.id                                             AS product_uom_id,
                    template.categ_id                                           AS product_categ_id,
                    line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                                                                                AS quantity,
                    -line.balance                                               AS price_subtotal,
                    -line.balance / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0)
                                                                                AS price_average,
                                                                                
                    COALESCE(partner.country_id, commercial_partner.country_id) AS country_id, 1 AS nbr_lines
            '''

    @api.model
    def _from(self):
        return '''
                FROM account_move_line line
                    LEFT JOIN res_partner partner ON partner.id = line.partner_id
                    LEFT JOIN product_product product ON product.id = line.product_id
                    LEFT JOIN account_account account ON account.id = line.account_id
                    LEFT JOIN account_account_type user_type ON user_type.id = account.user_type_id
                    LEFT JOIN product_template template ON template.id = product.product_tmpl_id
                    LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
                    LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
                    INNER JOIN account_move move ON move.id = line.move_id
                    LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
            '''

    @api.model
    def _where(self):
        return '''
                WHERE move.type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                    AND line.account_id IS NOT NULL
                    AND NOT line.exclude_from_invoice_tab
            '''

    @api.model
    def _group_by(self):
        return '''
                GROUP BY
                    line.id,
                    line.move_id,
                    line.product_id,
                    line.account_id,
                    line.analytic_account_id,
                    line.journal_id,
                    line.company_id,
                    line.currency_id,
                    line.partner_id,
                    move.name,
                    move.state,
                    move.type,
                    move.amount_residual_signed,
                    move.amount_total_signed,
                    move.partner_id,
                    move.invoice_user_id,
                    move.fiscal_position_id,
                    move.invoice_payment_state,
                    move.invoice_date,
                    move.invoice_date_due,
                    move.invoice_payment_term_id,
                    move.invoice_partner_bank_id,
                    uom_template.id,
                    uom_line.factor,
                    template.categ_id,
                    partner.x_city_id,
                    partner.state_id,
                    partner.township_id,
                    COALESCE(partner.country_id, commercial_partner.country_id)
            '''

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s %s %s %s
                )
            ''' % (
            self._table, self._select(), self._from(), self._where(), self._group_by()
        ))
