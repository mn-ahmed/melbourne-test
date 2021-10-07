from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'


    # znl 16 sept 2020
    customer_city_id = fields.Many2one('res.city', string='Customer City')
    customer_state_id = fields.Many2one('res.country.state', string='Customer State')
    customer_township_id = fields.Many2one('res.township', string='Customer Township')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):

        fields['customer_city_id'] = ', partner.x_city_id as customer_city_id'
        fields['customer_state_id'] = ', partner.state_id as customer_state_id'
        fields['customer_township_id'] = ', partner.township_id as customer_township_id'

        groupby += ',partner.x_city_id,partner.state_id,partner.township_id'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)




