from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    internal_po_no = fields.Char(string='Internal PO No')


class ProductCategory(models.Model):
    _inherit = "product.category"
    parent_id = fields.Many2one('product.category', ' Parent Brand', index=True, ondelete='cascade')

    def check_access_domain(self):

        return {
                'type': 'ir.actions.act_window',
                'name': ('Product Brand'),
                'res_model': 'product.category',
                'view_mode': 'tree,form'

                }




class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_id = fields.Many2one('res.partner')

    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([], limit=1)
        if category:
            return category.id
        else:
            err_msg = _('You must define at least one product category in order to be able to create products.')
            redir_msg = _('Go to Internal Categories')
            raise RedirectWarning(err_msg, self.env.ref('product.product_category_action_form').id, redir_msg)

    categ_id = fields.Many2one(
        'product.category', 'Brand',
        change_default=True, default=_get_default_category_id, group_expand='_read_group_categ_id',
        required=True, help="Select category for the current product")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_no = fields.Char(string='Invoice No')
    internal_po_no = fields.Char(string='Internal PO No')
    project_name = fields.Char(string='Project Name')


class PurchseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    brand_id = fields.Many2one('product.brand', string='Category ')

    @api.onchange('product_id')
    def _onchange_product(self):
        product_tempalte_obj = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
        self.brand_id = product_tempalte_obj.brand_id


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'
    category_id = fields.Many2one('product.category', 'Product Brand', readonly=True)
