from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    margin_percentage = fields.Float('GP Marginal', group_operator="avg")
    gp_margin_markup = fields.Float('GP Mark Up', group_operator="avg")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['margin_percentage'] = ", l.margin_percentage"
        fields['gp_margin_markup'] = ", l.gp_margin_markup"
        groupby += ', l.margin_percentage, l.gp_margin_markup'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

