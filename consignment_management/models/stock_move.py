from odoo import api, models, fields, _


class StockMove(models.Model):

    _inherit = 'stock.move'

    consignment_transfer_line_id = fields.Many2one('consignment.transfer.line', 'Consignment Transfer Line')
    consignment_return_line_id = fields.Many2one('consignment.transfer.line', 'Consignment Return Line')
