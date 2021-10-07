from odoo import api, models, fields, _


class StockWarehouse(models.Model):

    _inherit = 'stock.warehouse'

    is_consignment_warehouse = fields.Boolean('Consignment')
