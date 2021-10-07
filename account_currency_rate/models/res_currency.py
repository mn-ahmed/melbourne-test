import logging
import math
import re
import time
import traceback

from odoo import api, fields, models, tools, _
from odoo.tools.misc import get_lang


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    base_rate = fields.Float(digits=0, default=1.0, string='Base Rate', help='The rate of the base currency rate')

    @api.onchange('base_rate')
    def onchange_rate(self):
        if self.base_rate:
            self.rate = 1 / self.base_rate
