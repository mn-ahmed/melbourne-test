from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        branch = vals.get("branch_id", False)
        if branch:
            sequence_id = self.env['res.branch'].browse(branch).so_sequence_id
            if sequence_id:
                vals["name"] = sequence_id._next() or "/"
            else:
                raise UserError(_("Please define a sequence on your branch."))
        return super(SaleOrder, self).create(vals)

