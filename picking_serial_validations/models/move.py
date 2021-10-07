# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        # print("picking_serial_valiation")
        res = super(StockMove, self).write(vals)
        if 'move_line_nosuggest_ids' or 'move_line_ids' in vals:
            for move in self:
                if move.picking_code == 'incoming':
                    if len(move.move_line_nosuggest_ids) > move.product_uom_qty:
                        raise ValidationError(
                            _('You can insert only %s Lot/Serial Numbers!' % (
                                str(move.product_uom_qty))
                              )
                        )

                    if any(
                            len(l.lot_name) == 13
                            for l in move.move_line_nosuggest_ids.filtered(
                                lambda i: i.lot_name
                            )
                    ):
                        raise ValidationError(
                            _('Please enter serial number instead of Barcode')
                        )
                else:
                    if len(move.move_line_ids) > move.product_uom_qty:
                        raise ValidationError(
                            _('You can insert only %s Lot/Serial Numbers!' % (
                                str(move.product_uom_qty))
                              )
                        )

                    if any(
                            len(l.lot_name) == 13
                            for l in move.move_line_ids.filtered(
                                lambda i: i.lot_name
                            )
                    ):
                        raise ValidationError(
                            _('Please enter serial number instead of Barcode')
                        )
        return res

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder)
        for move in self:
            if move.picking_code == 'incoming':
                for ml in move.move_line_nosuggest_ids.filtered(lambda i: i.lot_name):
                    exist_lot = self.env['stock.production.lot'].sudo().search([('name', '=', ml.lot_name)])
                    if len(exist_lot) > 1:
                        raise ValidationError(
                            _('Lot Number : %s already exist!' % (ml.lot_name))
                        )
        return res


class StockMoveLine(models.Model):  # ZNL 21 OCT 2020
    _inherit = "stock.move.line"

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        check_company=True)#tha 28.10.2020

    @api.onchange('product_id')
    def _onchange_product(self):
        lot_ids = []
        if self.product_id:
            for rec in self:

                if rec.product_id:
                    name = self.env['stock.quant'].search(
                        [('product_id', '=', rec.product_id.id), ('location_id', '=', rec.location_id.id),
                         ('quantity', '>=', 1)])

                    if name:
                        for a in name.lot_id:
                            lot_ids.append(a.id)

                        return {'domain': {'lot_id': [('id', 'in', lot_ids)]}}
                    else:
                        return {'domain': {'lot_id': [('id', 'in', lot_ids)]}}

