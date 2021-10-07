# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import AccessError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sales_team_id = fields.Many2one(
        'crm.team',
        string="Default Sales Team",
        help="Selected team will be selected default on Sales Team Selection")

