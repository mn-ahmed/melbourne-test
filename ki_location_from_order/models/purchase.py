# -*- coding: utf-8 -*-

from odoo import models,fields,api

class PurchaseOrder(models.Model):
    _inherit='purchase.order'

    po_location_dest_id = fields.Many2one(
        'stock.location',
        string="Destination Location",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    def _get_destination_location(self):
        res = super(PurchaseOrder, self)._get_destination_location()
        self.ensure_one()
        if self.po_location_dest_id:
            return self.po_location_dest_id.id
        return res
