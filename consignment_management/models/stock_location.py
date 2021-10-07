from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):

    _inherit = 'stock.location'

    is_consignment_location = fields.Boolean('Consignment Location', default=False)

    @api.constrains('is_consignment_location', 'usage')
    def check_consignment_location(self):
        for rec in self:
            if rec.is_consignment_location and rec.usage != 'internal':
                raise ValidationError(_('Consignment location has to be an internal location.'))
