# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_branch_ids = fields.Many2many('res.branch', 'user_id', 'branch_id', string='Branch')
