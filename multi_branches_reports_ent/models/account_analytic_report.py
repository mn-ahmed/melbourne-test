# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AnalyticReport(models.AbstractModel):
    _inherit = 'account.analytic.report'

    filter_branch = None
