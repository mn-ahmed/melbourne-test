from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    street = fields.Char(string='Street', related='partner_id.street', )
    street2 = fields.Char(related='partner_id.street2', string='street2')
    township_id = fields.Many2one("res.township", related="partner_id.township_id", readonly=True, store=True)
    state_id = fields.Many2one('res.country.state', related="partner_id.state_id", readonly=True, store=True)
    city = fields.Char(related='partner_id.city', string='City', store=True)
    zip = fields.Char(related='partner_id.zip', string='zip')
    ph_no = fields.Char(related='partner_id.phone')
    country_id = fields.Many2one("res.country", related="partner_id.country_id", readonly=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.product_tmpl_id.product_description:
            name += '\n' + product_lang.product_tmpl_id.product_description

        return name
