from odoo import models, fields, api, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = "Res Partner Extension"

    vendor_code = fields.Char(string="Vendor Code", readonly=True, copy=False, store=True, index=True)

    @api.model
    def create(self, vals):
        if vals.get('supplier') == True:
            vals['vendor_code'] = str('V') + self.env['ir.sequence'].next_by_code('res.partner') or _('New')
        res = super(ResPartner, self).create(vals)
        return res

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res['country_id'] = 145
        return res
