# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    branch_id = fields.Many2one('res.branch', 'Branch')

    @api.model
    def create(self, values):
        res = super(PosSession, self).create(values)
        res.branch_id = self.env.user.branch_id.id or False
        return res
