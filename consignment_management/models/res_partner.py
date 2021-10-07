from odoo import api, models, fields, _


class Partner(models.Model):

    _inherit = 'res.partner'

    is_consignment_customer = fields.Boolean('Consignment', default=False)
    location_name = fields.Char('Location Name')
    consignment_location_id = fields.Many2one('stock.location', 'Consignment Location')

    @api.model
    def create(self, values):
        is_consignment_customer = values.get('is_consignment_customer', False)
        location_name = values.get('location_name') if values.get('location_name') else values.get('name')
        if not is_consignment_customer:
            return super(Partner, self).create(values)
        location_id = self.env['stock.location'].create({
            'name': location_name,
            'location_id': self.env.ref('stock.stock_location_locations').id,
            'usage': 'internal',
            'company_id': self.env.company.id,
            'is_consignment_location': True,
            'branch_id': values.get('branch_id', False)
        })
        values['customer'] = True
        values['location_name'] = location_name
        values['consignment_location_id'] = location_id.id
        return super(Partner, self).create(values)
