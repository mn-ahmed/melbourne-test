# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    lot_ids = fields.Many2many(
        'stock.production.lot', 'Lot/Serial Number',
        compute="_lot_domain_on_location", check_company=True)#tha 28.10.2020

    def _lot_domain_on_location(self):
        lot_ids = []
        for rec in self:
            name = self.env['stock.quant'].search(
                [('location_id', '=', rec.location_id.id),('quantity', '>=', 1)])

            if name:
                for a in name.lot_id:
                    lot_ids.append(a.id)

            rec.lot_ids = lot_ids#tha 28.10.2020
            
    def button_validate(self):
        self.user_id = self.env.user.id
        picking_type = self.picking_type_id
        if picking_type.code == 'outgoing':
            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = self.move_line_ids
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking == 'serial':
    
                        if not line.lot_id:
                            raise ValidationError(
                                _('Please enter valid Lot for Product: %s' %(product.display_name))
                            )
    
                        move = line.move_id
                        return_move = move.origin_returned_move_id
    
                        if return_move:
    
                            exist_orig_line = return_move.move_line_ids.filtered(
                                lambda i: i.lot_id == line.lot_id
                            )
        
                            if not exist_orig_line:
                                raise ValidationError(
                                    _('Lot Number: %s is does not exist or not belongs from original transfer!' %(line.lot_id.display_name))
                                )
                        if line.lot_id.sudo().product_qty <= 0.0:
                            raise ValidationError(
                                _('Lot Number: %s is does not have sufficient quantity to transfer!' %(line.lot_id.display_name))
                            )
        if self.partner_id:
            stat = """UPDATE stock_move SET partner_id='"""+str(self.partner_id.id)+"""' WHERE picking_id='"""+str(self.id)+"""';"""
            self.env.cr.execute(stat)

        res = super(StockPicking, self).button_validate()

        self.ensure_one()
        picking_type = self.picking_type_id
        if picking_type.code == 'incoming':

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = self.move_line_ids
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking == 'serial':
    
                        if not line.lot_id:
                            raise ValidationError(
                                _('Please enter valid Lot for Product: %s' %(product.display_name))
                            )
    
                        move = line.move_id
                        return_move = move.origin_returned_move_id
    
                        if return_move:
    
                            exist_orig_line = return_move.move_line_ids.filtered(
                                lambda i: i.lot_id == line.lot_id
                            )
        
                            if not exist_orig_line:
                                raise ValidationError(
                                    _('Lot Number: %s is does not exist or not belongs from original transfer!' %(line.lot_id.display_name))
                                )
                        if line.lot_id.sudo().product_qty <= 0.0:
                            raise ValidationError(
                                _('Lot Number: %s is does not have sufficient quantity to transfer!' %(line.lot_id.display_name))
                            )
        return res

class StockImmediateTransfer(models.TransientModel):
    _name = 'stock.immediate.transfer'
    _inherit = 'stock.immediate.transfer'


    def process(self):
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        for picking in self.pick_ids:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        if pick_to_do:
            pick_to_do.action_done()
            if pick_to_do.partner_id:
                stat = """UPDATE stock_move SET partner_id='"""+str(pick_to_do.partner_id.id)+"""' WHERE picking_id='"""+str(pick_to_do.id)+"""';"""
                self.env.cr.execute(stat)
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False
