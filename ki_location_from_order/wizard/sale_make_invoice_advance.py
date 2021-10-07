# -*- coding: utf-8 -*-

from odoo import models,fields,api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(
            SaleAdvancePaymentInv, self
        )._create_invoice(order, so_line, amount)
        if order.so_source_dest_id:
            invoice.so_source_dest_id = order.so_source_dest_id.id
        return invoice
