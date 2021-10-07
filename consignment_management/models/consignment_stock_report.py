from odoo import api, models, fields, _


class ConsignmentStockReport(models.Model):

    _name = 'consignment.stock.report'
    _description = 'Consignment Stock Report'
    _rec_name = 'date'

    date = fields.Date('Date')
    product_id = fields.Many2one('product.product', 'Product')
    partner_id = fields.Many2one('res.partner', 'Consignee')
    location_id = fields.Many2one('stock.location', 'Location')
    opening_qty = fields.Float('Opening Qty')
    transferred_qty = fields.Float('Transferred Qty')
    returned_qty = fields.Float('Returned Qty')
    ordered_qty = fields.Float('Ordered Qty')
    closing_qty = fields.Float('Closing Qty')
