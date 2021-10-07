from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_description = fields.Text(string='Product Description')




class ProductProduct(models.Model):
    _inherit = "product.product"

    product_description = fields.Text(string=' Product Description')

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        if self.product_tmpl_id.product_description:
            name += '\n' + self.product_tmpl_id.product_description

        return name
