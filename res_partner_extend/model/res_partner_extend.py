from odoo import api, models, fields, _


class Partner(models.Model):
    _inherit = 'res.partner'

    tag_id_custom = fields.Char(string='Tags', compute='_get_tags', store=True)

    @api.depends('category_id')
    def _get_tags(self):
        for rec in self:
            if rec.category_id:
                tag_custom = ','.join([p.name for p in rec.category_id])
            else:
                tag_custom = ''

            rec.tag_id_custom = tag_custom
