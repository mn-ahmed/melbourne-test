# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def _set_branch_on_location(self, branch):
        view_location = self.view_location_id
        child_locations = self.env['stock.location'].sudo().search([
            ('id', 'child_of',view_location.id)
        ])
        child_locations.write({'branch_id': branch})

    @api.model
    def create(self, vals):
        if self._context.get('is_branch'):
            return False
        warehouse = super(Warehouse, self).create(vals)
        if warehouse:
            warehouse.lot_stock_id.write({'branch_id': vals.get('branch_id')})
            warehouse.view_location_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_input_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_qc_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_output_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_pack_stock_loc_id.write({'branch_id': vals.get('branch_id')})

            if vals.get('branch_id', False):
                warehouse._set_branch_on_location(vals['branch_id'])

            # v12 base problem company not change in buy rule
#             warehouse.buy_pull_id.write({'company_id': vals.get('company_id')})
        return warehouse

    def write(self, vals):
        res= super(Warehouse, self).write(vals)
        if vals.get('branch_id', False):
            for warehouse in self:
                warehouse._set_branch_on_location(vals['branch_id'])
        return res