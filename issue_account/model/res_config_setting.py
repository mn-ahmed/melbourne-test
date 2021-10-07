# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_sample = fields.Boolean('Sample Issue', related='company_id.is_sample', readonly=False)
    sample_account_id = fields.Many2one('account.account', 'Sample Issue Account',
                                        related='company_id.sample_account_id', readonly=False)
    is_damage = fields.Boolean('Damage Issue', related='company_id.is_damage', readonly=False)
    damage_account_id = fields.Many2one('account.account', 'Damage Issue Account',
                                        related='company_id.damage_account_id', readonly=False)

    @api.onchange('company_id')
    def onchange_company_id(self):
        for res in self:
            res.is_sample = res.company_id.is_sample
            res.sample_account_id = res.company_id.sample_account_id
            res.is_damage = res.company_id.is_damage
            res.damage_account_id = res.company_id.damage_account_id
