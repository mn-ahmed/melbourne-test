from odoo import models, fields, api, _

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id_order_line(self):

        if not (self.partner_id and self.order_line):
            return

        partner_id = self.partner_id.id
        product_id = self.order_line.product_id.id

        prev_sale_orders = self.search([('partner_id', '=', partner_id)])

        if not prev_sale_orders:
            return

        order_lines = prev_sale_orders.mapped('order_line')

        order_lines = order_lines.filtered(lambda obj : obj.product_id.id == product_id)

        if not order_lines:
            return

        prev_price = order_lines.mapped('price_unit')

        if not prev_price:
            return

        self.order_line.price_unit = prev_price[0]

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_percentage = fields.Float(
        compute='_product_margin_percentage',
        digits='GP Marginal',
        store=True
    )
    gp_margin_markup = fields.Float(
        compute='_product_margin_percentage',
        digits='GP Mark Up',
        store=True
    )

    @api.depends(
        'product_id',
        'purchase_price',
        'product_uom_qty',
        'price_unit',
        'price_subtotal'
    )
    def _product_margin_percentage(self):
        for line in self:
            cost = line.product_id.standard_price
            line.margin_percentage = 0.0
            line.gp_margin_markup = 0.0
            if cost > 0:
                order_cur = line.order_id.currency_id
                order_comp_cur = line.order_id.company_id.currency_id
                #currency conversion company to order currency
                if order_cur != order_comp_cur:
                    cost = order_comp_cur._convert(
                        cost, order_cur,
                        line.order_id.company_id,
                        fields.Date.today()
                    )

                margin_percentage = 0.0
                if line.price_unit:
                    margin_percentage = (
                        (line.price_unit - cost) / line.price_unit
                    ) * 100.0
                line.margin_percentage = margin_percentage

                gp_margin_markup = 0.0
                if cost != 0.0:
                    gp_margin_markup = (
                        (line.price_unit - cost) / cost
                    ) * 100.0
                line.gp_margin_markup = gp_margin_markup
