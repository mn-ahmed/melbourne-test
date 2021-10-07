from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    sales_man_id = fields.Many2one(
        'hr.employee',
        string="Salesman",
        copy=False,
        track_visibility='onchange'
    )
    sale_by = fields.Many2one('hr.employee', string="Sales Person", track_visibility='always')
    sameple_damage = fields.Selection([('sample', 'Sample'),
                                       ('damage', 'Damage'), ], 'Sample/Damage', track_visibility='always')
    is_sample_created = fields.Boolean('Has the Sample Been Created?', default=False)
    is_damage_created = fields.Boolean('Has the Damage Been Created?', default=False)
    delivery_date = fields.Datetime(string='Sale Delivery Date', index=True, copy=False, default=fields.Datetime.now, )
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'confirm': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True)

    contact_id = fields.Char(string='Contact Name')
    contact_phone = fields.Char('Contact Phone')
    contact_address = fields.Char('Contact Address')
    accept_person = fields.Char(string='Accept Person')
    state = fields.Selection(selection_add=[('confirm', 'Sale Confirm')], string='Status', readonly=True, copy=False,
                             index=True, tracking=3, default='draft')

    street = fields.Char(string='Street', related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2', string='street2')
    township_id = fields.Many2one("res.township", related="partner_id.township_id", readonly=True, store=True)
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id', readonly=True, store=True)
    city = fields.Char(related='partner_id.city', string='City', store=True)
    zip = fields.Char(related='partner_id.zip', string='zip')
    ph_no = fields.Char(related='partner_id.phone')
    country_id = fields.Many2one("res.country", related="partner_id.country_id", readonly=True)
    department_id = fields.Many2one('hr.department',string='Department')
    do_name = fields.Char(string='DO Name',compute='_get_do_name')

    def _get_do_name(self):
        for rec in self:
            if rec.name is not None:
                rec.do_name = self.env['stock.picking'].search([('origin', '=', self.name)], limit=1).name
            else:
                rec.do_name=False
    @api.onchange('sale_by')
    def onchange_employee(self):
        for rec in self:
            rec.department_id = rec.sale_by.department_id.id

    def action_sale_confirm(self):
        self.write({'state': 'confirm'})

    def _prepare_invoice(self):
        self.ensure_one()
        values = super(SaleOrder, self)._prepare_invoice()
        values.update({
            'sales_man_id': self.sales_man_id.id,
            'sale_by': self.sale_by.id,
            'contact_id': self.contact_id,
            'accept_person': self.accept_person,
            'contact_phone': self.contact_phone,
            'contact_address': self.contact_address
        })
        return values

    def create_sample(self):
        vals = self.get_sale_order_data()
        self.env['sample.give'].create(vals)
        self.write({'is_sample_created': True})

    def create_damage(self):
        vals = self.get_sale_order_data()
        vals['issued_date'] = vals.pop('sample_give_date')
        del vals['return_date']
        self.env['damage.product'].create(vals)
        self.write({'is_damage_created': True})

    def get_sale_order_data(self):
        order_lines = []
        stock_picking = self.mapped('picking_ids')[0]
        for order_line in self.order_line:
            product_id = order_line.product_id.id
            product_description = order_line.name
            product_uom_qty = order_line.product_uom_qty
            order_lines.append(
                (0, 0, {
                    'product_id': product_id,
                    'product_description': product_description,
                    'product_uom_qty': product_uom_qty,
                })
            )
        if not order_lines:
            order_lines = False
        return {
            'partner_id': self.partner_id.id,
            'picking_type_id': stock_picking.picking_type_id.id,
            'location_id': stock_picking.location_id.id,
            'branch_id': stock_picking.branch_id.id,
            'sample_give_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': (datetime.now() + relativedelta(months=1)).strftime('%Y-%m-%d'),
            'sale_person': self.user_id.id,
            'mr_no': self.name,
            'team_id': self.team_id.id,
            'sale_by': self.sale_by.id,
            'accept_person': self.accept_person,
        }

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for do_pick in self.picking_ids:
            do_pick.write({'mr_no': self.name})
            do_pick.write({'customer_name': self.partner_id.id})
            do_pick.write({'branch_id': self.branch_id.id})
            do_pick.write({'team_id': self.team_id.id})
            do_pick.write({'sale_person': self.user_id.id})
            do_pick.write({'sale_by': self.sale_by.id})
            do_pick.write({'delivery_date': self.delivery_date})
            do_pick.write({'contact_person': self.contact_id})
            do_pick.write({'contact_phone': self.contact_phone})
            do_pick.write({'contact_address': self.contact_address})
            do_pick.write({'accept_person': self.accept_person})
            do_pick.write({'transfer_type': 'sale',
                           'sale_remark': self.note})

        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_sale_order_line_multiline_description_sale(self,product):

        """ Compute a default multiline description for this sales order line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return product.get_product_multiline_description_sale()
