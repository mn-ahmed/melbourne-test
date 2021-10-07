# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api


class Company(models.Model):
    _inherit = 'res.company'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        context = dict(self.env.context)
        if context.get('company_id', None):
            company_id = self.env.company
            args = (args or []) + [('id', '=', company_id.id)]
        return super(Company, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
