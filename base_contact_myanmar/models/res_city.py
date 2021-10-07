from odoo import api, fields, models


class ResCity(models.Model):
    _name = "res.city"
    _description = 'Cities'

    name = fields.Char(string='Cities Name', required=True)
    code = fields.Char(string='Cities Code')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')

    @api.onchange('state_id')
    def onchange_state(self):
        self.country_id = self.state_id.country_id
