# -*- coding: utf-8 -*-

from odoo import models,fields,api


class StockLocation(models.Model):
    _inherit='stock.location'

    @api.model
    def _search(self, args, offset=0, limit=None,
            order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('picking_type_code', ''):
            if not args:
                args = []
            args += [('usage', '=', 'internal'), ('active', '=', True)]
        return super(
            StockLocation, self
        )._search(args, offset, limit, order,
            count=count, access_rights_uid=access_rights_uid
        )


class StockPicking(models.Model):
    _inherit='stock.picking'

    location_dest_id = fields.Many2one(
        states={
            'draft': [('readonly', False)],
            'waiting': [('readonly', False)],
            'confirmed': [('readonly', False)],
            'assigned': [('readonly', False)]
        }
    )
    location_id = fields.Many2one(
        states={
            'draft': [('readonly', False)],
            'waiting': [('readonly', False)],
            'confirmed': [('readonly', False)],
            'assigned': [('readonly', False)]
        }
    )
    picking_type_id = fields.Many2one(
        states={
            'draft': [('readonly', False)],
            'waiting': [('readonly', False)],
            'confirmed': [('readonly', False)],
            'assigned': [('readonly', False)]
        }
    )

    @api.model
    def create(self, values):
        if 'origin' in values:
            so = self.env['sale.order'].sudo().search([('name', '=', values['origin'])])
            if so and so.so_source_dest_id:
                values['location_id'] = so.so_source_dest_id.id
        picking = super(StockPicking, self).create(values)
        picking.onchange_location_dest()
        return picking

    @api.onchange('location_dest_id', 'location_id')
    def onchange_location_dest(self):
        for picking in self:
            if (picking.location_dest_id and picking.picking_type_code == 'incoming') or (picking.location_dest_id and not picking.location_id):
                domain = [
                    ('default_location_dest_id', '=', picking.location_dest_id.id),
                    ('warehouse_id.company_id', '=', picking.company_id.id),
                    ('code', '=', 'incoming')
                ]
                picking_type = self.env['stock.picking.type'].sudo().search(domain, limit=1)
                if picking_type:
                    picking.picking_type_id = picking_type

                for move in picking.move_ids_without_package:
                    for ml in move.move_line_ids:
                        ml.update({'location_dest_id' : picking.location_dest_id.id})

                for move in picking.move_line_ids:
                    move.update({'location_dest_id' : picking.location_dest_id.id})
            elif picking.location_id and picking.picking_type_code != 'incoming':
                domain = [
                    ('default_location_src_id', '=', picking.location_id.id),
                    ('warehouse_id.company_id', '=', picking.company_id.id),
		    ('code', '=', 'outgoing')
                ]
                picking_type = self.env['stock.picking.type'].sudo().search(domain, limit=1)
                if picking_type:
                    picking.picking_type_id = picking_type

    def write(self, values):
        res = super(StockPicking, self).write(values)
        if values.get('location_dest_id', False):
            for picking in self:
                for move in picking.move_ids_without_package:
                    for ml in move.move_line_ids:
                        ml.write({'location_dest_id' : picking.location_dest_id.id})
        if values.get('location_id', False):
            for picking in self:
                for move in picking.move_ids_without_package:
                    for ml in move.move_line_ids:
                        ml.write({'location_id' : picking.location_id.id})
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        self.ensure_one()
        for ml in self.move_line_ids:
            ml.location_dest_id = self.location_dest_id.id
        return super(StockMove, self).action_show_details()


class StockPickingType(models.Model):
    _inherit='stock.picking.type'

    def _search(self, args, offset=0, limit=None,
            order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if not args:
                args = []

        picking_type_code = context.get('picking_type_code', '')
        location_dest_id = context.get('location_dest_id', False)
        location_id = context.get('location_id', False)

        if picking_type_code == 'incoming' and location_dest_id:
            args += [('default_location_dest_id', '=', location_dest_id)]
        elif location_id:
            args += [('default_location_src_id', '=', location_dest_id)]

        return super(
            StockPickingType, self
        )._search(args, offset, limit, order,
            count=count, access_rights_uid=access_rights_uid
        )
