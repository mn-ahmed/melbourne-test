# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class AccountMove(models.Model):
    _inherit = "account.move"

    sales_team_id = fields.Many2one(
        'crm.team',
        string="Default Sales Team",
        copy=False,
        states={
            'draft': [('readonly', False)]
        },
        readonly=True
    )
    sales_man_id = fields.Many2one(
        'hr.employee',
        string="Sales Man",
        copy=False,
        states={
            'draft': [('readonly', False)]
        },
        readonly=True
    )
    helper_id  = fields.Many2one(
        'hr.employee',
        string="Helper",
        copy=False,
        states={
            'draft': [('readonly', False)]
        },
        readonly=True
    )

