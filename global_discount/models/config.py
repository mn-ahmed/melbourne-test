from odoo import models, fields, api


class Company(models.Model):
    _inherit = "res.company"

    apply_discount = fields.Boolean(string="Activate Discount")
    sales_discount_account_id = fields.Many2one('account.account', string="Sales Discount Account")
    purchase_discount_account_id = fields.Many2one('account.account', string="Purchase Discount Account")

    account_sale_incl_tax_id = fields.Many2one('account.tax', string="Default Sale Tax(Inclusive)")
    account_purchase_incl_tax_id = fields.Many2one('account.tax', string="Default Purchase Tax(Inclusive)")
    
    sale_tax_excl_id = fields.Many2one('account.tax', string="Default Sale Tax(Exclusive)", )
    purchase_tax_excl_id = fields.Many2one('account.tax', string="Default Purchase Tax(Exclusive)")

    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_discount = fields.Boolean(string="Activate Discount", related='company_id.apply_discount', readonly=False)
    sales_discount_account_id = fields.Many2one('account.account', string="Sales Discount Account", related='company_id.sales_discount_account_id', readonly=False)
    purchase_discount_account_id = fields.Many2one('account.account', string="Purchase Discount Account", related='company_id.purchase_discount_account_id', readonly=False)
    
    sale_tax_incl_id = fields.Many2one('account.tax', string="Default Sale Tax(Inclusive)", related='company_id.account_sale_incl_tax_id', readonly=False)
    purchase_tax_incl_id = fields.Many2one('account.tax', string="Default Purchase Tax(Inclusive)", related='company_id.account_purchase_incl_tax_id', readonly=False)

    sale_tax_excl_id = fields.Many2one('account.tax', string="Default Sale Tax(Exclusive)", related='company_id.sale_tax_excl_id', readonly=False)
    purchase_tax_excl_id = fields.Many2one('account.tax', string="Default Purchase Tax(Exclusive)", related='company_id.purchase_tax_excl_id', readonly=False)
