# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
	_inherit = 'stock.move'

	qty_available = fields.Float('Product On Hand', related='product_id.qty_available')
	inventory_quantity = fields.Float('Location On Hand', compute='_compute_location_onhand')
	remark = fields.Text("Remark")
	picking_type_code = fields.Selection([
		('incoming', 'Vendors'),
		('outgoing', 'Customers'),
		('internal', 'Internal')], related='picking_id.picking_type_code', string='Sample/Demage Picking Code', readonly=True)

	@api.depends('product_id')
	def _compute_location_onhand(self):
		self.inventory_quantity = 0.0
		for line in self:
			if line.picking_type_code == 'outgoing' or line.picking_type_code == 'internal':
				stock_quant = self.env['stock.quant'].search(
					[('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)], limit=1)
				line.inventory_quantity = stock_quant.quantity
			elif line.picking_type_code == 'incoming':
				stock_quant = self.env['stock.quant'].search(
					[('product_id', '=', line.product_id.id), ('location_id', '=', line.location_dest_id.id)], limit=1)
				line.inventory_quantity = stock_quant.quantity

	@api.onchange('product_id')
	def onchange_product_on_location(self):
		for line in self:
			if line.picking_id.picking_type_code == 'outgoing' or line.picking_id.picking_type_code == 'internal':
				stock_quant = self.env['stock.quant'].search(
					[('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)], limit=1)
				line.inventory_quantity = stock_quant.quantity
			elif line.picking_id.picking_type_code == 'incoming':
				stock_quant = self.env['stock.quant'].search(
					[('product_id', '=', line.product_id.id), ('location_id', '=', line.location_dest_id.id)], limit=1)
				line.inventory_quantity = stock_quant.quantity