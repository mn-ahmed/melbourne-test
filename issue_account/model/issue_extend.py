from odoo import api, fields, models, _


class SaleSampleGive(models.Model):
    _inherit = 'sample.give'

    is_sample = fields.Boolean("Sample", default=True)


class SaleSampleGiveLine(models.Model):
    _inherit = 'sample.give.line'

    is_sample = fields.Boolean("Sample", related='give_id.is_sample')


class SaleDamage(models.Model):
    _inherit = 'damage.product'

    is_damage = fields.Boolean("Sample", default=True)


class SaleDamageGiveLine(models.Model):
    _inherit = 'damage.product.line'

    is_damage = fields.Boolean("Sample", related='damaged_id.is_damage')
