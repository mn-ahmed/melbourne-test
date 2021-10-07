# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'

    brand_id = fields.Many2one('product.brand', string=' Category')

    @api.onchange('product_id')
    def _onchange_product(self):
        product_tempalte_obj = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
        self.brand_id = product_tempalte_obj.brand_id


class SaleReport(models.Model):
    _inherit = 'sale.report'

    categ_id = fields.Many2one('product.category', 'Product Brand ', readonly=True)
