# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    _description = 'Return Picking'

    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        if self.picking_id.transfer_type == 'sample':
            new_picking = self.picking_id.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': _("Sample Return of %s") % self.picking_id.name,
                'transfer_type': 'sample_return',
                'location_id': self.picking_id.location_dest_id.id,
                'location_dest_id': self.location_id.id})
        elif self.picking_id.transfer_type == 'damage_delivery':
            new_picking = self.picking_id.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': _("Damage Delivery of %s") % self.picking_id.name,
                'transfer_type': 'damage_receipt',
                'location_id': self.picking_id.location_dest_id.id,
                # 'scheduled_date': self.issued_date,
                'location_dest_id': self.location_id.id})
        elif self.picking_id.transfer_type == 'sale':
            new_picking = self.picking_id.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': _("Return of %s") % self.picking_id.name,
                'transfer_type': 'sale_return',
                'location_id': self.picking_id.location_dest_id.id,
                'location_dest_id': self.location_id.id})
        elif self.picking_id.transfer_type == 'purchase':
            new_picking = self.picking_id.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': _("Return of %s") % self.picking_id.name,
                'transfer_type': 'purchase_return',
                'location_id': self.picking_id.location_dest_id.id,
                'location_dest_id': self.location_id.id})
        else:
            new_picking = self.picking_id.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': _("Return of %s") % self.picking_id.name,
                'transfer_type': 'normal',
                'location_id': self.picking_id.location_dest_id.id,
                'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(return_line, new_picking)
                r = return_line.move_id.copy(vals)
                vals = {}

                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]
                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking.action_confirm()
        new_picking.action_assign()

        for move in new_picking.move_lines:
            return_picking_line = self.product_return_moves.filtered(
                lambda r: r.move_id == move.origin_returned_move_id)
            if return_picking_line and return_picking_line.to_refund:
                move.to_refund = True

        return new_picking.id, picking_type_id