from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_open_quants(self):
        self.env['stock.quant']._merge_quants()
        self.env['stock.quant']._unlink_zero_quants()
        products = self.mapped('product_variant_ids')
        action = self.env.ref('stock_onhand_internal.product_open_quants').read()[0]
        action['domain'] = [('product_id', 'in', products.ids)]
        action['context'] = {'search_default_internal_loc': 1}
        return action