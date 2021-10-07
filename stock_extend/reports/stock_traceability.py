# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.tools import config


rec = 0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec


class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'
    _description = 'Traceability Report'

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = []
        reference = False
        cashier = False
        sale_man = False
        for data in final_vals:
            if data.get('reference_id'):
                reference = data.get('reference_id')
            print("reference",reference)
            origin = self.env['stock.picking'].search([('name','=',reference)]).origin
            pos_obj = self.env['pos.order'].search([('name','=',origin)])
            
            cashier = pos_obj.employee_id.name
            sale_man = pos_obj.sales_man_id.name
            
            
            lines.append({
                'id': autoIncrement(),
                'model': data['model'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'usage': data.get('usage', False),
                'is_used': data.get('is_used', False),
                'lot_name': data.get('lot_name', False),
                'lot_id': data.get('lot_id', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            data.get('product_id', False),
                            data.get('date', False),
                            data.get('lot_name', False),
                            data.get('location_source', False),
                            data.get('location_destination', False),
                            data.get('product_qty_uom', 0),
                            cashier,
                            sale_man],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines