# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_sample = fields.Boolean('Sample Issue')
    sample_account_id = fields.Many2one('account.account', 'Sample Issue Account')
    is_damage = fields.Boolean('Damage Issue')
    damage_account_id = fields.Many2one('account.account', 'Damage Issue Account')

