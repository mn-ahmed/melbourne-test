# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api


class BrandProduct(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char(String="Name")
    short_code = fields.Char(string='Short Code')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name Already Exit!'),
    ]


class ProductBrand(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string='Category')
    short_code = fields.Char(string='Short Code', related='brand_id.short_code')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string='Category', related="product_tmpl_id.brand_id", store=True)
    short_code = fields.Char(string='Short Code', related='brand_id.short_code', store=True)


class BrandReportStock(models.Model):
    _inherit = 'stock.quant'

    brand_id = fields.Many2one(related='product_id.brand_id',
                               string='Category', store=True, readonly=True)
