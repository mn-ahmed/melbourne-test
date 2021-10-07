from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ConsignmentTransferWizard(models.Model):

    _name = 'consignment.transfer.wizard'
    _description = 'Consignment Transfer Wizard'

    partner_id = fields.Many2one('res.partner', 'Consignee')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    type = fields.Selection([('order', 'Order'),
                             ('return', 'Return')], 'Type')
    line_ids = fields.One2many('consignment.transfer.line', 'transfer_wizard_id', 'Transfer Lines')

    def btn_order(self):

        consignment_transfer = self.env['consignment.transfer'].browse(self.env.context.get('active_id'))
        if not consignment_transfer:
            raise UserError(_('There is no active consignment transfer.'))

        line_values = []
        for line in self.line_ids:
            if line.to_order <= 0:
                continue
            if line.to_order > line.qty_left:
                raise UserError('Your order quantity can\'t be greater than the quantity left.')
            line_values.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.to_order,
                    'product_uom': line.product_id.uom_id.id,
                    'price_unit': line.price_unit,
                    'transfer_line_id': line.id,
                })
            )

        if not line_values:
            raise UserError(_('Please add at least a line.'))

        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'branch_id': self.partner_id.branch_id.id,
            'validity_date': fields.Date.today(),
            'backdate': fields.Datetime.now(),
            'delivery_date': fields.Datetime.now(),
            'date_order': fields.Datetime.now(),
            'warehouse_id': self.env.ref('consignment_management.consignment_warehouse').id,
            'consignment_sale': True,
            'from_transfer': True,
            'consignment_ref': consignment_transfer.name,
            'consignment_transfer_id': consignment_transfer.id,
            'order_line': line_values,
            'from_consignment_menu': True,
        })
        order.onchange_partner_id()
        order.onchange_partner_shipping_id()

        self.line_ids.write({
            'to_order': 0,
            'to_return': 0,
        })

        return True

    def btn_return(self):

        consignment_transfer = self.env['consignment.transfer'].browse(self.env.context.get('active_id'))
        self.ensure_one()
        lines = []

        if not self.line_ids:
            raise UserError(_('Please add at least a line.'))

        for line in self.line_ids:
            if line.to_return <= 0:
                continue
            if line.to_return > line.qty_left:
                raise UserError('Your return quantity can\'t be greater than the quantity left.')
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.to_return,
                    'price_unit': line.price_unit,
                    'discount_type': line.discount_type,
                    'discount_amt': line.discount_amt,
                    'price_subtotal': line.price_unit * line.to_return ,
                    'transfer_line_id': line.id,
                })
            )
        consignment_return = self.env['consignment.return'].create({
            'date': fields.Date.today(),
            'partner_id': consignment_transfer.partner_id.id,
            'warehouse_id': consignment_transfer.warehouse_id.id,
            'pricelist_id': consignment_transfer.pricelist_id.id,
            'branch_id': consignment_transfer.branch_id.id,
            'currency_id': consignment_transfer.currency_id.id,
            'transfer_id': consignment_transfer.id,
            'line_ids': lines,
            'state': 'draft',
        })
        consignment_return._compute_amount()

        self.line_ids.write({
            'to_order': 0,
            'to_return': 0,
        })
