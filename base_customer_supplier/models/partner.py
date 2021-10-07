from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = "res.partner"

    customer = fields.Boolean(string='Is a Customer', 
                              help="Check this box if this contact is a customer. It can be selected in sales orders.")
    supplier = fields.Boolean(string='Is a Vendor', 
                              help="Check this box if this contact is a vendor. It can be selected in purchase orders.")