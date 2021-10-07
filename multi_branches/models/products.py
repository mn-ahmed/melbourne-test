from odoo import models, fields, api, _


class ProductsTemplate(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2one("res.branch", string='Branch')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            # if len(branches) > 0:
            #     self.branch_id = branches[0]
            # else:
            #     self.branch_id = False
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}


class Products(models.Model):
    _inherit = 'product.product'

    branch_id = fields.Many2one("res.branch", string='Branch')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            # if len(branches) > 0:
            #     self.branch_id = branches[0]
            # else:
            #     self.branch_id = False
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        if self.company_id:
            book = self.env['product.template'].search([('branch_id', '=', self.branch_id.id)], limit=1)
            self.branch_id = book and book.id
        else:
            return {'domain': {'branch_id': []}}

class ProductCategory(models.Model):
    _inherit = 'product.category'

    branch_id = fields.Many2one('res.branch', string='Branch')
