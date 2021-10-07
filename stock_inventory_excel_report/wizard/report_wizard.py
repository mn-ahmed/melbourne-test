# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
import xlwt
import time
from odoo import models, api, fields, _
from odoo.exceptions import Warning
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class inventory_reports(models.TransientModel):
    _name = 'report.in.out.wizard'
    _description = 'Report In/Out Wizard'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='warehouse'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location'
    )
    start_date = fields.Date(
        string='Beginning Date',
        required=True,
        default=lambda *a: (parser.parse(datetime.now().strftime('%Y-%m-%d')) + relativedelta(days=-1)).strftime(
            '%Y-%m-%d')
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        default=lambda *a: time.strftime('%Y-%m-%d')
    )
    sort_order = fields.Selection(
        selection=[
            ('warehouse', 'Location'),
            ('product_brand', 'Product Brand')
        ],
        string='Group By',
        required=True,
        default='warehouse'
    )
    include_zero = fields.Boolean(
        string='Include Zero Movement?',
    )
    filter_product_ids = fields.Many2many(
        'product.product',
        string='Products'
    )
    filter_product_categ_ids = fields.Many2many(
        'product.category',
        string='Categories'
    )
    display_all_products = fields.Boolean(
        string='Display Products?',
        default=True
    )

    branch_id = fields.Many2one('res.branch', string='Branch', required=True,
                                default=lambda self: self.env.user.branch_id)

    @api.onchange('sort_order')
    def onchange_sortorder(self):
        if self.sort_order == 'warehouse':
            self.filter_product_categ_ids = False
        elif self.sort_order == 'product_category':
            self.filter_product_ids = False
        else:
            self.filter_product_categ_ids = False
            self.filter_product_ids = False

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        warehouse_ids = self.env['stock.warehouse'].sudo().search([])
        if self.branch_id:
            warehouse_ids = self.env['stock.warehouse'].sudo().search([('branch_id', '=', self.branch_id.id)])
        return {
            'domain':
                {
                    'warehouse_ids': [('id', 'in', [x.id for x in warehouse_ids])]
                },
            'value':
                {
                    'warehouse_ids': False
                }
        }


    @api.onchange('company_id')
    def onchange_company_id(self):
        warehouse_ids = self.env['stock.warehouse'].sudo().search([])
        if self.company_id:
            warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.company_id.id)])
        return {
            'domain':
                {
                    'warehouse_ids': [('id', 'in', [x.id for x in warehouse_ids])]
                },
            'value':
                {
                    'warehouse_ids': False
                }
        }

    @api.onchange('warehouse_ids')
    def onchange_warehouse(self):
        location_obj = self.env['stock.location']
        location_ids = location_obj.search([('usage', '=', 'internal')])
        total_warehouses = self.warehouse_ids
        if total_warehouses:
            addtional_ids = []
            for warehouse in total_warehouses:
                store_location_id = warehouse.view_location_id.id
                addtional_ids.extend([y.id for y in location_obj.search(
                    [('location_id', 'child_of', store_location_id), ('usage', '=', 'internal')])])
            location_ids = addtional_ids
        else:
            location_ids = [p.id for p in location_ids]
        return {
            'domain':
                {
                    'location_id': [('id', 'in', location_ids)]
                },
            'value':
                {
                    'location_id': False
                }
        }

    def action_export_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'inventory.in.out.reports'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref(
                'stock_inventory_excel_report.inventory_io_report_xlsx'
            ).report_action(self, data=datas)
