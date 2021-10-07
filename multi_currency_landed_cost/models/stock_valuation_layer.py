# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = 'stock.valuation.layer'

    multi_stock_landed_cost_id = fields.Many2one('multi.stock.landed.cost', 'Multi Landed Cost')

