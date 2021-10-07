from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    consignment_ref = fields.Char('Transfer Reference')
    consignment_transfer_id = fields.Many2one('consignment.transfer', 'Consignment Transfer')
    from_transfer = fields.Boolean('From Transfer')
    consignment_sale = fields.Boolean('Consignment Order')
    from_consignment_menu = fields.Boolean('From Consignment Menu?')

    @api.constrains('consignment_sale', 'warehouse_id')
    def check_consignment_warehouse(self):
        for rec in self:
            if rec.consignment_sale and not rec.warehouse_id.is_consignment_warehouse:
                raise ValidationError(_('Your selected warehouse is not consignment warehouse.'))

    @api.constrains('consignment_sale', 'partner_id')
    def check_consignment_warehouse(self):
        for rec in self:
            if rec.consignment_sale != rec.partner_id.is_consignment_customer:
                raise ValidationError(_('Please check your consignment checkbox and customer.'))

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id.is_consignment_customer:
            self.warehouse_id = self.env.ref('consignment_management.consignment_warehouse').id
        return res

    @api.onchange('from_consignment_menu')
    def onchange_from_consignment_menu(self):
        if self.from_consignment_menu:
            domain = [('customer', '=', True), ('is_consignment_customer', '=', True)]
        else:
            domain = [('customer', '=', True), ('is_consignment_customer', '!=', True)]
        return {'domain': {'partner_id': domain}}

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.ensure_one()
        if not self.consignment_sale:
            return res
        for line in self.order_line:
            transfer_line = line.transfer_line_id
            prev_ordered_qty = transfer_line.ordered_qty
            prev_qty_left = transfer_line.qty_left
            transfer_line.write({
                'ordered_qty': prev_ordered_qty + line.product_uom_qty,
                'qty_left': prev_qty_left - line.product_uom_qty,
            })
        self.picking_ids.write({
            'location_id': self.partner_id.consignment_location_id.id,
        })
        return res


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    transfer_line_id = fields.Many2one('consignment.transfer.line', 'Consignment Transfer Line')


