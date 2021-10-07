# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from itertools import groupby


class SaleDamage(models.Model):
    _name = 'damage.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Damage Product Received'

    name = fields.Char('Name',track_visibility='always',copy=False,default='New')
    state = fields.Selection([
        ('new','New'),
        ('submit', 'Submitted'),
        ('apporved', 'Approved'),
        ('confirm', 'Confirmed'),
        ('ordered','Damaged Ordered'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='new',track_visibility='always')

    mr_no = fields.Char(string='MR No',track_visibility='always')
    partner_id = fields.Many2one('res.partner',string='Customer Name',track_visibility='always')
    accept_person = fields.Char(string='Accept Person')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False, readonly=True,
        states={'new': [('readonly', False)]},domain=[('code', 'in', ('outgoing','incoming'))])
    location_id = fields.Many2one('stock.location',string='Location Name',
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        track_visibility='always',readonly=True,Store=True)
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        track_visibility='always',readonly=True,Store=True)
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code',
        readonly=True)
    damaged_remark = fields.Text(string="Remark")
    sale_person = fields.Many2one('res.users',string='Sale By',track_visibility='always',default=lambda self:self.env.user.id)
    issued_date = fields.Date(string='Issued Date',default=fields.Date.today(),track_visibility='always')
    branch_id = fields.Many2one('res.branch',string='Branch',track_visibility='always',default=lambda self: self.env.user.branch_id)

    product_line = fields.One2many('damage.product.line', 'damaged_id', string='Product Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    
    picking_ids = fields.One2many('stock.picking', 'damaged_id', string='Pickings')
    received_count = fields.Integer(string='Delivery', compute='_compute_picking_ids',store=True)
    company_id= fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id)

    team_id = fields.Many2one('crm.team', 'Sales Team')
    sale_by = fields.Many2one('hr.employee','Sale Person', track_visibility='always')
    delivery_status = fields.Selection([('not', 'Not Delivered'),
                                        ('partial', 'Partially Delivered'),
                                        ('full', 'Fully Delivered')], 'Delivery Status',
                                       compute='compute_delivery_status')

    def compute_delivery_status(self):
        for rec in self:
            if all([line.deliver_qty == 0 for line in rec.product_line]):
                rec.delivery_status = 'not'
            elif all([line.deliver_qty == line.product_uom_qty for line in rec.product_line]):
                rec.delivery_status = 'full'
            else:
                rec.delivery_status = 'partial'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids

            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    @api.onchange('branch_id')
    def _onchange_branch_id(self):

        if self.branch_id:
            warehouse = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
            picking = self.env['stock.picking.type'].search(
                [('warehouse_id', 'in', warehouse.ids)])
            if self.branch_id and picking:
                self.picking_type_id = picking.ids[0]

            else:
                self.picking_type_id = False

            return {'domain': {'picking_type_id': [('id', '=', picking.ids)]}}


        else:
            return {'domain': {'picking_type_id': []}}
    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('damage.product') or _('New')
        res = super(SaleDamage, self).create(vals)
        return res

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.received_count = len(order.picking_ids)

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            elif self.partner_id:
                location_dest_id = self.partner_id.property_stock_customer.id
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

            if self.state == 'new':
                self.location_id = location_id
                self.location_dest_id = location_dest_id

    def action_submit(self):
        self.state = 'submit'

    def action_approved(self):
        self.state = 'apporved'

    def action_confirm(self):
        self.state = 'confirm'

    def action_check(self):
        self.state = 'check'

    def action_cancel(self):
        self.state = "cancel"
        self.picking_ids = False

    def action_set_to_new(self):
        self.state = 'new'

    def action_confirmed(self):
        self.state = 'ordered'
        deli_id = self.partner_id.id
        lines = self.product_line

        if not lines:
            raise UserError('Please add at least one line!')

        # Check if all lines have picking types
        picking_types_in_all_lines = all([line.picking_type_id.id for line in lines])
        if not picking_types_in_all_lines:
            raise UserError('Some of the lines do not have operation types!')

        # Check if all lines have the same picking type (incoming, outgoing)
        picking_code = lines[0].picking_type_id.code
        same_picking_types = all([line.picking_type_id.code == picking_code for line in lines])
        if not same_picking_types:
            raise UserError('Operation types must be of same code!')

        lines = sorted(lines, key=lambda l: l.picking_type_id)

        for picking_type, damage_lines in groupby(lines, key=lambda l: l.picking_type_id):

            picking_values = {}
            move_values = {}

            if picking_type.code == 'incoming':
                location_id = picking_type.default_location_dest_id
                picking_values.update({
                    'location_id': self.env.ref('stock.stock_location_suppliers').id,
                    'location_dest_id': location_id.id,
                    'transfer_type': 'damage_receipt',
                })
                move_values.update({
                    'location_id': self.env.ref('stock.stock_location_suppliers').id,
                    'location_dest_id': location_id.id,
                })
            else:
                location_id = picking_type.default_location_src_id
                picking_values.update({
                    'location_id': location_id.id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'transfer_type': 'damage_delivery',
                })
                move_values.update({
                    'location_id': location_id.id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                })

            if not location_id:
                raise UserError('Please check the operation types.\n'
                                'Some of those do not have the required location.')

            picking_values.update({
                'picking_type_id': picking_type.id,
                'customer_name': self.partner_id.id,
                'partner_id': deli_id,
                'company_id': self.company_id.id,
                'origin': self.name,
                'damaged_id': self.id,
                'mr_no': self.mr_no,
                'sale_person': self.sale_person.id,
                'issued_date': self.issued_date,
                'branch_id': self.branch_id.id,
                'damaged_remark': self.damaged_remark,
                'team_id': self.team_id.id,
                'sale_by': self.sale_by.id,
                'accept_person': self.accept_person,
            })

            picking = self.env['stock.picking'].create(picking_values)

            for product_line in list(damage_lines):
                move_values.update({
                    'name': self.name,
                    'product_id': product_line.product_id.id,
                    'picking_id': picking.id,
                    'product_uom': product_line.product_uom.id,
                    'product_uom_qty': product_line.product_uom_qty,
                    'remark': product_line.remark,
                    'description_picking': product_line.product_description,
                })
                self.env['stock.move'].create(move_values)

            picking.action_confirm()

    def action_view_receipt(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action


class SaleSampleGiveLine(models.Model):
    _name = 'damage.product.line'
    _description = 'Damaged Product Line'

    damaged_id = fields.Many2one('damage.product', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    image_small = fields.Binary("Product Image", related="product_id.image_1920")
    product_description = fields.Char(string='Description',related="product_id.product_tmpl_id.name")
    product_uom = fields.Many2one('uom.uom', 'UOM',related='product_id.uom_id',required=False)
    product_uom_qty = fields.Float(
        'Request Qty', default=1.0,
        digits='Product Unit of Measure', required=True)
    issued_qty = fields.Float(
        'Issue Qty', default=1.0,
        digits='Product Unit of Measure')
    remark = fields.Text(string='Remark')

    inventory_quantity = fields.Float('Qty available',compute='compute_inventory_quantity')

    deliver_qty = fields.Integer("Deliver Qty")
    return_qty = fields.Integer('Return Qty')
    balance_qty = fields.Integer('Balance Qty')
    product_brand_id = fields.Many2one('product.brand', string='Category')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      domain=[('code', 'in', ['incoming', 'outgoing'])])

    def compute_inventory_quantity(self):
        for line in self:
            stock_quant = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','=',line.damaged_id.location_id.id)],limit=1)
            line.inventory_quantity = stock_quant.quantity

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.product_brand_id = self.product_id.brand_id