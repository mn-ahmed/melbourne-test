from odoo import models, fields, api, _
from datetime import date


class Partner(models.Model):
    _inherit = "res.partner"


    sequence_id = fields.Char(string="Customer Code", readonly=True, copy=False, store=True, index=True)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        if vals.get('customer') == True:
            if res.state_id and not res.sequence_id:
                self.sequence_id = str(self.state_id.name) +  str(self.env['ir.sequence'].next_by_code('res.partner') or _('New'))



        return res

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        if vals.get('customer') == True:
            if res.state_id and not res.sequence_id:
                sequence_ids = self.env['res.country.state'].browse(vals['state_id']).sequence_id
                if sequence_ids:
                    state_code = sequence_ids.prefix
                    res.sequence_id = str(state_code) + str(self.env['ir.sequence'].next_by_code('res.partner') or _('New'))
        return res

    def generate_sequence_code(self):
        for partner in self:
            if partner.customer is True:
                sequence_ids= partner.state_id.sequence_id
                state_code = sequence_ids.prefix
                partner.sequence_id = str(state_code) + str(self.env['ir.sequence'].next_by_code('res.partner') or _('New'))
