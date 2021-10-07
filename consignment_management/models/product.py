from odoo import api, models, fields, _


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    consignment_ok = fields.Boolean('Can be sold for Consignment', default=True)

