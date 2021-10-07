# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount_type = fields.Selection(
        selection=[
            ('amount', "Fixed"),
            ('percent', "Percentage")
        ],
        default="amount",
        string="Type",
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )
    discount_rate = fields.Float(
        string="Discount",
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )
    amount_discount_global = fields.Monetary(
        string='Global Discount',
        store=True,
        readonly=True,
#         compute='_amount_all',
        track_visibility='always'
    )
    amount_discount_line = fields.Monetary(
        string='Line Discount',
        store=True,
        readonly=True,
        compute='_amount_all',
        track_visibility='always'
    )
    amount_total_line_disc = fields.Monetary(
        string='After Line Discount',
        store=True,
        readonly=True,
        compute='_amount_all'
    )
    amount_total_global_disc = fields.Monetary(
        string='After Global Discount',
        store=True,
        readonly=True,
        compute='_amount_all',
        track_visibility='always'
    )
    amount_total_after_tax = fields.Monetary(
        string='Total After Tax',
        store=True,
        readonly=True,
        compute='_amount_all',
        track_visibility='always'
    )
    total_discount_amount = fields.Float(
        'Total Line Discount Amount',
        readonly=True,
        store=True,
        compute='_amount_all')#THA 17.9.2020

    @api.depends(
        'order_line.price_total',
        'discount_type',
        'discount_rate',
    )
    def _amount_all(self):
        super(SaleOrder, self)._amount_all()
        for order in self:

            amount_discount_line = 0.0
            amount_untaxed = amount_tax = 0.0
            total_discount_amount = 0.0

            for line in order.order_line:
                amount_untaxed += line.price_total
                amount_discount_line += (
                        line.price_subtotal - (line.price_unit * line.product_uom_qty)
                )
            amount_total_after_tax = amount_untaxed
            amount_tax = 0.0

            # total_discount_amount = sum((l.product_uom_qty * l.discount_amount) for l in order.order_line)#THA 17.9.2020
            # order.total_discount_amount = total_discount_amount#THA 17.9.2020

            tmp_amount_untaxed = 0.0
            #11.8.2020
            for line in self.order_line:
                tmp_total = line.price_unit*line.product_uom_qty

                line_discount = 0.0
                if line.discount_type == 'fixed':
                    line_discount = line.product_uom_qty * line.discount_amount
                    total_discount_amount += line_discount
                else:
                    line_discount = tmp_total * (line.discount_amount/100)
                    total_discount_amount += line_discount

                tmp_price_subtotal = tmp_total - line_discount

                for tax in line.tax_id:
                    if tax.price_include != True:
                        tx = tmp_price_subtotal *(tax.amount/100)
                        tmp_price_subtotal = tmp_price_subtotal# + tx
                        amount_tax += tx
                    else:
                        tx = tmp_price_subtotal /((100+tax.amount ) / tax.amount)
                        amount_tax += tx
                        tmp_price_subtotal = tmp_price_subtotal - tx

                tmp_amount_untaxed += tmp_price_subtotal
            amount_total_after_tax = tmp_amount_untaxed + amount_tax

            amount_discount_global = 0.0

            if order.discount_type:
                if order.discount_type == 'amount':
                    amount_discount_global = order.discount_rate
                else:
                    amount_discount_global = (
                        amount_total_after_tax * order.discount_rate
                    ) / 100.00

            amount_total_line_disc = amount_untaxed

            order.update({
                'amount_untaxed': tmp_amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total_after_tax - amount_discount_global,
                'total_discount_amount': total_discount_amount,
                'amount_discount_line': amount_discount_line,
                'amount_total_line_disc': tmp_amount_untaxed ,
                'amount_discount_global': amount_discount_global,
                'amount_total_global_disc': amount_total_after_tax - amount_discount_global,
                'amount_total_after_tax': amount_total_after_tax
            })

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
            'total_discount_amount' : self.total_discount_amount,#THA 17.9.2020
        })
        return res

    def _create_invoices(self, grouped=False, final=False):
        moves = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        for line in moves.mapped('invoice_line_ids'):
            line.onchange_discount_type()
        return moves

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_type = fields.Selection(
        selection=[
            ('fixed', "Fixed"),
            ('percentage', 'Percentage')
        ],
        default="fixed",
    )
    discount_amount = fields.Float(
        string="Discount",
    )

    @api.depends(
        'product_uom_qty',
        'discount', 'price_unit',
        'tax_id',
        'discount_amount',
        'discount_type',
    )
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            if line.discount_type:
                price = line.price_unit
                discount = line.discount_amount

                line_discount = 0.0
                tmp_total = line.price_unit * line.product_uom_qty
                if line.discount_type == 'fixed':
                    line_discount += (line.product_uom_qty * line.discount_amount)
                else:
                    line_discount += tmp_total *(line.discount_amount/100)

                price_stotal = (line.price_unit * line.product_uom_qty) - line_discount
                taxes = line.tax_id.compute_all(
                    price_stotal,
                    line.order_id.currency_id,
                    1,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id
                )
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({
            'discount_type': self.discount_type,
            'discount_amount': self.discount_amount,
        })
        discount = 0.0
        if self.discount_type and self.discount_amount:
            if self.discount_type == 'fixed':
                discount = (
                    100.00 * (self.product_uom_qty * self.discount_amount)
                ) / (self.price_unit * self.product_uom_qty)


            else:
                discount = self.discount_amount
        res.update({
            "discount": discount
        })
        
        return res

