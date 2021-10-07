# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    @api.depends(
        'order_line.price_total' ,
        'discount_type',
        'discount_rate',
    )
    def _amount_all(self):
        for order in self:

            amount_discount_line = 0.0
            amount_untaxed = amount_tax = 0.0
            tmp_price_subtotal = tmp_amount_untaxed = tmp_total = 0.0
            amount_tax = 0.0
            total_line_discount = 0.0
            line_discount = 0.0 

            #11.8.2020 THA
            for line in self.order_line:
                tmp_total = line.price_unit * line.product_qty
                if line.discount_type == 'fixed':
                    tmp_price_subtotal = tmp_total - (line.discount_amount*line.product_qty)
                    line_discount = line.discount_amount*line.product_qty
                    total_line_discount += line_discount
                else:
                    tmp_price_subtotal = tmp_total - (tmp_total *(line.discount_amount/100))
                    line_discount = tmp_total *(line.discount_amount/100)
                    total_line_discount += line_discount

                if line.taxes_id:
                    for tax in line.taxes_id:
                        if tax.price_include != True:
                            tmp_price_subtotal = line.price_subtotal
                            tt = line.price_subtotal * (tax.amount / 100)
                            amount_tax += round(tt, 2)
                            amount_untaxed += tmp_price_subtotal #line.price_subtotal
                        else:
                            tx = tmp_price_subtotal / ((100 + tax.amount) / tax.amount)
                            amount_tax += round(tx, 2)
                            tmp_price_subtotal = tmp_price_subtotal - tx  # (tmp_price_subtotal/((100+tax.amount ) / tax.amount))
                            amount_untaxed += round(tmp_price_subtotal, 2)
                else:
                    amount_untaxed += tmp_price_subtotal

                tmp_amount_untaxed += tmp_total
                line.amount_untaxed = amount_untaxed
                line.price_subtotal = tmp_price_subtotal
                line.line_discount = line_discount
                
                tmp_price_subtotal = 0.0
                line_discount = 0.0

            amount_total_after_tax = amount_untaxed + amount_tax

            amount_discount_global = 0.0
            
            if order.discount_type:
                if order.discount_type == 'amount':
                    amount_discount_global = order.discount_rate
                else:
                    amount_discount_global = (
                        amount_total_after_tax * order.discount_rate
                    ) / 100.00

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'total_line_discount': total_line_discount,
                'amount_total': amount_total_after_tax  - amount_discount_global,
                'amount_discount_line': amount_discount_line,
                'amount_total_line_disc': amount_untaxed,
                'amount_discount_global': amount_discount_global,
                'amount_total_global_disc': amount_total_after_tax + amount_tax - amount_discount_global,
                'amount_total_after_tax': amount_total_after_tax
            })


    discount_type = fields.Selection(
        selection=[
            ('amount', "Fixed"),
            ('percent', "Percentage")
        ],
        default="amount",
        string="Type",
        readonly=False,
        states={
            'purchase': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    discount_rate = fields.Float(
        string="Discount",
        readonly=False,
        states={
            'purchase': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    amount_discount_global = fields.Monetary(
        string='Global Discount',
        store=True,
        readonly=True,
        compute='_amount_all',
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
    total_line_discount = fields.Float('Total Line Discount',readonly=True)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_type = fields.Selection(
        selection=[
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed')
        ],
        default="fixed",
    )
    discount_amount = fields.Float(
        string="Discount",
    )
    line_discount = fields.Float(string="Line Discount Amount")
    amount_untaxed = fields.Float(string="Line Amount Untaxed")

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount_type', 'discount_amount')
    def _compute_amount(self):
        return super(PurchaseOrderLine, self)._compute_amount()

    def _prepare_compute_all_values(self):
        res = super(PurchaseOrderLine, self)._prepare_compute_all_values()
        price_unit = res['price_unit']
        product_qty = res['product_qty']
        
        if self.discount_type == 'percentage':
            price_unit = price_unit * (1 - (self.discount_amount or 0.0) / 100.0)
        else:
            price_unit = (price_unit * product_qty) - (self.discount_amount*product_qty)#11.8.2020 THA
            product_qty = 1.0
            
        res['price_unit'] = price_unit
        res['product_qty'] = product_qty
        return res

    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({
            'discount_type': self.discount_type,
            'discount_amount':  self.discount_amount,
        })
        return res
