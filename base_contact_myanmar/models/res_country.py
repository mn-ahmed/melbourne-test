import re
import logging
from odoo import api, fields, models
from odoo.osv import expression
from psycopg2 import IntegrityError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Country(models.Model):
    _inherit = 'res.country'

    township_id = fields.Many2one('res.township', string='Township', ondelete='restrict')

    address_format = fields.Text(string="Layout in Reports",
                                 help="Display format to use for addresses belonging to this country.\n\n"
                                      "You can use python-style string pattern with all the fields of the address "
                                      "(for example, use '%(street)s' to display the field 'street') plus"
                                      "\n%(township_name)s: the name of the township"
                                      "\n%(state_name)s: the name of the state"
                                      "\n%(state_code)s: the code of the state"
                                      "\n%(country_name)s: the name of the country"
                                      "\n%(country_code)s: the code of the country",
                                 default='%(street)s\n%(street2)s\n%(township_name)s %(city)s\n%(state_code)s %(zip)s\n%(country_name)s')

    def get_address_fields(self):
        self.ensure_one()
        return re.findall(r'\((.+?)\)', self.address_format)

    @api.constrains('address_format')
    def _check_address_format(self):
        for record in self:
            if record.address_format:
                address_fields = self.env['res.partner']._formatting_address_fields() + ['township_name', 'state_code',
                                                                                         'state_name', 'country_code',
                                                                                         'country_name', 'company_name']
                try:
                    record.address_format % {i: 1 for i in address_fields}
                except (ValueError, KeyError):
                    raise UserError(_('The layout contains an invalid format key'))