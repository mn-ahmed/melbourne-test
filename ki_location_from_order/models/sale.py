# -*- coding: utf-8 -*-

from odoo import models,fields,api

class SaleOrder(models.Model):
    _inherit='sale.order'

    so_source_dest_id = fields.Many2one(
        'stock.location',
        string="Source Location",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    def _prepare_invoice(self):
        self.ensure_one()
        values = super(SaleOrder, self)._prepare_invoice()
        if self.so_source_dest_id:
            values.update({'so_source_dest_id': self.so_source_dest_id.id})
        return values
