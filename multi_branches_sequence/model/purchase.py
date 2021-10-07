from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        branch = vals.get("branch_id", False)
        if branch:
            sequence_id = self.env['res.branch'].browse(branch).po_sequence_id
            if sequence_id:
                vals["name"] = sequence_id._next() or "/"
            else:
                raise UserError(_("Please define a sequence on your branch."))
        return super(PurchaseOrder, self).create(vals)



