from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ConsignmentReturn(models.Model):

    _name = 'consignment.return'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Consignment Return'

    name = fields.Char('Reference', default='Draft', copy=False, tracking=0)
    date = fields.Datetime('Date', default=fields.Datetime.now, tracking=1)
    partner_id = fields.Many2one('res.partner', 'Consignee', tracking=2)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', tracking=3)
    pricelist_id = fields.Many2one('product.pricelist', 'Price List', tracking=4)
    currency_id = fields.Many2one('res.currency', 'Currency', related='pricelist_id.currency_id', store=True)
    line_ids = fields.One2many('consignment.transfer.line', 'consignment_return_id', 'Return Lines')
    picking_ids = fields.One2many('stock.picking', 'consignment_return_id', 'Pickings')
    transfer_id = fields.Many2one('consignment.transfer', 'Consignment Transfer')
    amount_total = fields.Monetary('Total')
    delivery_count = fields.Integer('Delivery Count', compute='compute_delivery_count', store=False)
    branch_id = fields.Many2one('res.branch', 'Branch', tracking=5)
    user_id = fields.Many2one('res.users', 'Responsible Person',
                              default=lambda self: self.env.user.id, tracking=6)
    transfer_ref = fields.Char('Transfer Reference', related='transfer_id.name', store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('deliver', 'Delivered'),
                              ('cancel', 'Cancelled')], default='draft')

    def compute_delivery_count(self):
        for rec in self:
            rec.delivery_count = len(rec.picking_ids)

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

    @api.model
    def create(self, values):
        if values.get('name') == 'Draft' or not values.get('name'):
            values['name'] = self.env['ir.sequence'].sudo().next_by_code('consignment.return')
        return super(ConsignmentReturn, self).create(values)

    def action_view_delivery(self):

        picking_ids = self.picking_ids

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
                    'consignment_return_line_id': line.id,
                })
            )

        picking = self.env['stock.picking'].create({
            'location_dest_id': self.warehouse_id.lot_stock_id.id,
            'location_id': self.partner_id.consignment_location_id.id,
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id,
            'scheduled_date': self.date,
            'origin': self.name,
            'branch_id': self.partner_id.branch_id.id,
            'company_id': self.env.company.id,
            'move_lines': move_values,
            'consignment': True,
            'consignment_return_id': self.id,
        })

        picking.action_confirm()
        self.write({'state': 'confirm'})

    def btn_cancel(self):
        self.ensure_one()
        for picking in self.picking_ids:
            picking.action_cancel()
        self.state = 'cancel'
