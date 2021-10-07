# -*- coding: utf-8 -*-

from odoo import models,fields,api


class Move(models.Model):
    _inherit='account.move'

    so_source_dest_id = fields.Many2one(
        'stock.location',
        string="Source Location",
        readonly=True,
    )
    po_location_dest_id = fields.Many2one(
        'stock.location',
        string="Destination Location",
    )