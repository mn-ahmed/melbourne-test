from odoo import models, fields

class ResUsers(models.Model):

    _inherit = 'res.users'

    so_allow_back_date = fields.Boolean('Allow SO Back Date?')
    so_allow_current_date = fields.Boolean('Allow SO Current Date?')
    so_allow_future_date = fields.Boolean('Allow SO Future Date?')
    so_back_days = fields.Integer('SO Backdate Limit(Days)')

    po_allow_back_date = fields.Boolean('Allow PO Back Date?')
    po_allow_current_date = fields.Boolean('Allow PO Current Date?')
    po_allow_future_date = fields.Boolean('Allow PO Future Date?')
    po_back_days = fields.Integer('PO Backdate Limit(Days)')

    invoice_allow_back_date = fields.Boolean('Allow INV Back Date?')
    invoice_allow_current_date = fields.Boolean('Allow INV Current Date?')
    invoice_allow_future_date = fields.Boolean('Allow INV Future Date?')
    invoice_back_days = fields.Integer('INV Backdate Limit(Days)')