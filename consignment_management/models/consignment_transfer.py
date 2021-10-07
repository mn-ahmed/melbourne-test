from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ConsignmentTransfer(models.Model):

    _name = 'consignment.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Consignment Transfer'

    def get_default_branch(self):
        return self.env['res.branch'].search([('name', '=', 'SUN Mobile 1 Branch')], order='id desc', limit=1).id

    name = fields.Char('Reference', default='Draft', copy=False, tracking=0)
    date = fields.Datetime('Date', default=fields.Datetime.now, tracking=1)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', tracking=2)
    partner_id = fields.Many2one('res.partner', 'Consignee', tracking=3)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', tracking=4)
    line_ids = fields.One2many('consignment.transfer.line', 'consignment_transfer_id', 'Transfer Lines')
    picking_ids = fields.One2many('stock.picking', 'consignment_transfer_id', 'Pickings')
    return_ids = fields.One2many('consignment.return', 'transfer_id', 'Returns')
    order_ids = fields.One2many('sale.order', 'consignment_transfer_id', 'Orders')
    currency_id = fields.Many2one('res.currency', 'Currency', related='pricelist_id.currency_id', store=True)
    amount_total = fields.Monetary('Total')
    delivery_count = fields.Integer('Delivery Count', compute='compute_picking_counts', store=False)
    return_count = fields.Integer('Return Count', compute='compute_return_count', store=False)
    order_count = fields.Integer('Order Count', compute='compute_order_count', store=False)
    branch_id = fields.Many2one('res.branch', 'Branch', tracking=5)
    user_id = fields.Many2one('res.users', 'Responsible Person', default=lambda self: self.env.user.id, tracking=6)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('deliver', 'Delivered'),
                              ('close', 'Closed'),
                              ('cancel', 'Cancelled')], default='draft')

    street = fields.Char(string='Street',related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2',string='street2')
    township_id = fields.Many2one("res.township",related="partner_id.township_id",readonly=True)
    city = fields.Char(related='partner_id.city',string='City')
    zip = fields.Char(related='partner_id.zip',string='zip')
    ph_no = fields.Char(related='partner_id.phone')
    country_id = fields.Many2one("res.country",related="partner_id.country_id",readonly=True)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.branch_id = self.partner_id.branch_id.id
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist.id
        else:
            self.pricelist_id = self.env.ref('product.list0', raise_if_not_found=False).id

    @api.onchange('line_ids')
    def _compute_amount(self):
        for rec in self:
            rec.update({
                'amount_total': sum([line.price_subtotal for line in rec.line_ids])
            })

    def compute_picking_counts(self):
        for rec in self:
            delivery_picking_ids = rec.picking_ids.filtered(lambda picking:
                                                             picking.location_dest_id.is_consignment_location is True)
            return_picking_ids = rec.picking_ids.filtered(lambda picking:
                                                           picking.location_id.is_consignment_location is True)
            rec.delivery_count = len(delivery_picking_ids)
            rec.return_count = len(return_picking_ids)

    def compute_return_count(self):
        for rec in self:
            rec.return_count = len(rec.return_ids)

    def compute_order_count(self):
        self.order_count = len(self.order_ids)

    @api.model
    def create(self, values):
        if values.get('name') == 'Draft' or not values.get('name'):
            values['name'] = self.env['ir.sequence'].sudo().next_by_code('consignment.transfer')
        return super(ConsignmentTransfer, self).create(values)

    def action_view_delivery(self):

        picking_ids = self.picking_ids.filtered(lambda picking:
                                                picking.location_dest_id.is_consignment_location is True)

        if len(picking_ids) > 1:
            action = {
                'name': 'Delivery',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', picking_ids.ids)],
            }
        elif len(picking_ids) == 1:
            action = {
                'name': 'Delivery',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': picking_ids.id,
            }
        else:
            action = {}
        return action

    def action_view_orders(self):

        order_ids = self.order_ids

        if len(order_ids) > 1:
            action = {
                'name': 'Orders',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', order_ids.ids)],
            }
        elif len(order_ids) == 1:
            action = {
                'name': 'Order',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id': order_ids.id,
            }
        else:
            action = {}
        return action

    def action_view_return(self):

        return_ids = self.return_ids.ids

        if len(return_ids) > 1:
            action = {
                'name': 'Return',
                'type': 'ir.actions.act_window',
                'res_model': 'consignment.return',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', return_ids)],
            }
        elif len(return_ids) == 1:
            action = {
                'name': 'Return',
                'type': 'ir.actions.act_window',
                'res_model': 'consignment.return',
                'view_mode': 'form',
                'res_id': return_ids[0],
            }
        else:
            action = {}
        return action

    def btn_confirm(self):

        self.ensure_one()
        move_values = []

        if not self.line_ids:
            raise UserError(_('Please add at least a line.'))

        picking_type = self.env['stock.picking.type'].search([('warehouse_id', '=', self.warehouse_id.id),
                                                              ('code', '=', 'internal')], order='id desc', limit=1)

        if not picking_type:
            raise UserError(_('Your selected warehouse doesn\' have internal transfer operation. '
                              'Please create one first.'))

        for line in self.line_ids:
            move_values.append(
                (0, 0, {
                    'name': self.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.quantity,
                    'description_picking': line.product_id.name,
                    'consignment_transfer_line_id': line.id,
                })
            )

        picking = self.env['stock.picking'].create({
            'location_id': self.warehouse_id.lot_stock_id.id,
            'location_dest_id': self.partner_id.consignment_location_id.id,
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id,
            'scheduled_date': self.date,
            'origin': self.name,
            'branch_id': self.partner_id.branch_id.id,
            'company_id': self.env.company.id,
            'move_lines': move_values,
            'consignment': True,
            'consignment_transfer_id': self.id,
        })

        picking.action_confirm()
        self.write({'state': 'confirm'})

    def btn_order(self):

        self.ensure_one()
        if all(list(map(lambda line: line.qty_left == 0, self.line_ids))):
            raise UserError('There is no quantity to order.')

        context = dict(self.env.context)
        line_ids = self.line_ids.filtered(lambda l: l.qty_left > 0).ids
        if not line_ids:
            raise UserError(_('There is no quantity left to order.'))
        context.update({
            'default_type': 'order',
            'default_partner_id': self.partner_id.id,
            'default_warehouse_id': self.warehouse_id.id,
            'default_line_ids': [(6, 0, line_ids)],
        })
        return {
            'name': 'Consignment Order',
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.transfer.wizard',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }

    def btn_return(self):

        self.ensure_one()
        if all(list(map(lambda line: line.qty_left == 0, self.line_ids))):
            raise UserError('There is no quantity to return.')

        context = dict(self.env.context)
        line_ids = self.line_ids.filtered(lambda l: l.qty_left > 0).ids
        if not line_ids:
            raise UserError(_('There is no quantity left to return.'))
        context.update({
            'default_type': 'return',
            'default_partner_id': self.partner_id.id,
            'default_warehouse_id': self.warehouse_id.id,
            'default_line_ids': [(6, 0, line_ids)],
        })
        return {
            'name': 'Consignment Return',
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.transfer.wizard',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }

    def btn_cancel(self):
        self.ensure_one()
        for picking in self.picking_ids:
            picking.action_cancel()
        self.state = 'cancel'


class ConsignmentTransferLine(models.Model):

    _name = 'consignment.transfer.line'
    _description = 'Consignment Transfer Line'

    product_id = fields.Many2one('product.product', 'Product')
    quantity = fields.Float('Quantity')
    delivered_qty = fields.Float('Delivered Quantity')
    returned_qty = fields.Float('Returned Quantity')
    qty_left = fields.Float('Quantity to be Ordered')
    ordered_qty = fields.Float('Ordered Quantity')
    price_unit = fields.Monetary('Unit Price')
    discount_type = fields.Selection([('fixed', 'Fixed'),
                                      ('percentage', 'Percentage')], 'Discount Type', default='fixed')
    discount_amt = fields.Float('Discount Amount')
    line_discount = fields.Monetary('Line Discount')
    price_subtotal = fields.Monetary('Subtotal')
    currency_id = fields.Many2one('res.currency', 'Currency', related='consignment_transfer_id.currency_id', store=True)
    to_order = fields.Float('To Order')
    to_return = fields.Float('To Return')
    consignment_transfer_id = fields.Many2one('consignment.transfer', 'Consignment Transfer')
    transfer_wizard_id = fields.Many2one('consignment.transfer.wizard', 'Consignment Transfer Wizard')
    consignment_return_id = fields.Many2one('consignment.return', 'Consignment Return')
    transfer_line_id = fields.Many2one('consignment.transfer.line', 'Consignment Transfer Line')

    @api.onchange('price_unit', 'quantity', 'discount_type', 'discount_amt')
    def _compute_line_amount(self):
        total_amt = self.price_unit * self.quantity
        if self.discount_type == 'fixed':
            discount = self.discount_amt * self.quantity
        else:
            discount = total_amt * (self.discount_amt/100)
        self.update({
                'line_discount': discount,
                'price_subtotal': total_amt - discount,
            })

    def write(self, values):
        res = super(ConsignmentTransferLine, self).write(values)
        for rec in self:
            transfer = rec.consignment_transfer_id
            if transfer and \
                    all(map(lambda l: l.qty_left == 0, transfer.line_ids)) and \
                    transfer.state == 'deliver':
                transfer.state = 'close'
        return res
