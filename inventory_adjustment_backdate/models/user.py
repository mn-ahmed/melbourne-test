# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class User(models.Model):
    _inherit = "res.users"

    allow_current_date = fields.Boolean(
        string="Only allow current date transaction",
        copy=False
    )
    allow_back_date = fields.Boolean(
        string="Only allow back X day transaction",
        copy=False
    )
    allow_future_date = fields.Boolean(
        string="Only allow to do future transaction",
        copy=False
    )
    back_date_limit = fields.Integer(
        string="Back Date Limit",
        copy=False
    )
