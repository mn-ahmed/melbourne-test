# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _


class ReportConsolidatedJournal(models.AbstractModel):
    _inherit = "account.consolidated.journal"

    filter_branch = None
