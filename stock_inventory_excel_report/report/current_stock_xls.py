# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models, _


class StockReportXls(models.AbstractModel):
    _name = 'report.stock_inventory_excel_report.stock_io_report_xlsx.xlsx'
    _description = 'Stock I/O Report'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        company = self.env.user.company_id
        company_id = data.get('form', {}).get('company_id', False)
        if company_id:
            company = self.env['res.company'].sudo().browse(company_id)

        product_obj = self.env['product.product'].sudo()

        y_offset = 0

        sheet = workbook.add_worksheet('Inventory Report')
        format0 = workbook.add_format({
            'bold': True, 'align': 'center', 'font_size': 14
        })
        format1 = workbook.add_format({
            'bold': True, 'bg_color': '#FFFFCC', 'border': True, 'align': 'left'
        })
        format2 = workbook.add_format({'border': True, 'align': 'left', })
        format5 = workbook.add_format({'align': 'left', 'bold': True, 'top': True})
        format5_2 = workbook.add_format({'align': 'left', 'bold': True})
        format5_1 = workbook.add_format({'align': 'left', })
        format5_border_top = workbook.add_format({'align': 'left', 'top': True})
        format3 = workbook.add_format({
            'align': 'center', 'bold': True, 'border': True
        })
        format4 = workbook.add_format({'border': True, 'align': 'left'})
        font_size_8 = workbook.add_format({'border': True, 'align': 'center'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 25)
        sheet.set_column('I:I', 25)
        sheet.set_column('F:F', 25)
        sheet.set_column('K:K', 25)
        sheet.set_column('L:L', 25)
        sheet.set_column('M:M', 25)
        sheet.set_column('N:N', 25)
        sheet.set_column('O:O', 25)
        sheet.merge_range(y_offset, 0, y_offset, 1, _('Inventory On Hand Report'), format0)
        y_offset += 2

        company_name = warehouse_name = location_name = ''
        company_name = company.name

        warehouse_id = data['form']['warehouse_ids']
        if warehouse_id:
            for warehouse in self.env['stock.warehouse'].browse(warehouse_id).name_get():
                warehouse_name += str(warehouse[1]) + ','
            warehouse_name = warehouse_name[:-1]
        else:
            warehouse_name = 'All'

        location_name = "All"
        if data['form']['location_id']:
            location_name = self.env['stock.location'].browse(data['form']['location_id']).display_name

        sheet.write(y_offset, 0, _('Company Name:'), format1)
        sheet.write(y_offset, 1, company_name or '', format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Warehouse Name:'), format1)
        sheet.write(y_offset, 1, warehouse_name or '', format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Location Name:'), format1)
        sheet.write(y_offset, 1, location_name, format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('From Date:'), format1)
        sheet.write(y_offset, 1, data['form']['start_date'] or '', format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('To Date:'), format1)
        sheet.write(y_offset, 1, data['form']['end_date'] or '', format2)
        y_offset += 1

        sheet.write(9, 0, 'No', format3)
        sheet.write(9, 1, 'Name', format3)
        sheet.write(9, 2, 'Category', format3)
        sheet.write(9, 3, 'Brand', format3)
        sheet.write(9, 4, 'Internal Reference', format3)
        sheet.write(9, 5, 'Beginning', format3)
        sheet.write(9, 6, 'Purchase Qty', format3)
        sheet.write(9, 7, 'Purchase Return', format3)
        sheet.write(9, 8, 'Sale Qty', format3)
        sheet.write(9, 9, 'Sale Return', format3)
        sheet.write(9, 10, 'POS qty', format3)
        sheet.write(9, 11, 'POS Return', format3)
        sheet.write(9, 12, 'Internal Transfer', format3)
        sheet.write(9, 13, 'Adjustment ', format3)
        sheet.write(9, 14, 'Scrap ', format3)
        sheet.write(9, 15, 'Closing Qty ', format3)

        if data.get('form', {}).get('sort_order', '') != 'product_category':
            report_obj = self.env['report.stock_inventory_excel_report.stock_report_by_warehouse']
            lines = report_obj._get_lines_xls(data, company.id)

            grand_total_begin = 0.0
            grand_total_in = 0.0
            grand_total_in_return = 0.0
            grand_total_out = 0.0
            grand_total_out_return = 0.0
            grand_total_pos = 0.0
            grand_total_pos_return = 0.0
            grand_total_int = 0.0
            grand_total_adj = 0.0
            grand_total_scrap = 0.0
            grand_total_end_qty = 0.0
            y_offset = 10
            for warehouse in lines.items():
                warehouse_name = report_obj._get_warehouse(warehouse[0])
                
                column = 0
                for location in warehouse[1]:
                    # location_name = self.env['stock.location'].browse(location)
                    location_name = self.env['stock.location'].search([('id', '=', location),('usage','=','internal')])
                    # sheet.write(y_offset,column, location_name.display_name, format5_2)

                    if not location_name:
                        continue

                    total_begin = 0.0
                    total_in = 0.0
                    total_in_return = 0.0
                    total_out = 0.0
                    total_out_return = 0.0
                    total_pos = 0.0
                    total_pos_return = 0.0
                    total_int = 0.0
                    total_adj = 0.0
                    total_scrap = 0.0
                    total_end_qty = 0.0
                    i = 1
                    for l in warehouse[1][location]:
                        sheet.write(y_offset, 0, i, format5_1)
                        product = product_obj.browse(l['product_id'])
                        prod_name = product.name_get()[0][1]
                        sheet.write(y_offset, 1, prod_name, format5_1)
                        sheet.write(y_offset, 2, product.brand_id.name or ' _ ', format5_1)
                        sheet.write(y_offset, 3, product.categ_id.name, format5_1)
                        sheet.write(y_offset, 4, product.default_code or '', format5_1)
                        begin_qty = report_obj._get_beginning_inventory(data, warehouse[0], l['product_id'], l) or 0.0
                        sheet.write(y_offset, 5, begin_qty, format5_1)
                        sheet.write(y_offset, 6, l['product_qty_in'], format5_1)
                        sheet.write(y_offset, 7, l['product_qty_in_return'], format5_1)
                        sheet.write(y_offset, 8, l['product_qty_out'], format5_1)
                        sheet.write(y_offset, 9, l['product_qty_out_return'], format5_1)
                        sheet.write(y_offset, 10, l['pos_qty'], format5_1)
                        sheet.write(y_offset, 11, l['pos_return_qty'], format5_1)
                        sheet.write(y_offset, 12, l['product_qty_internal'], format5_1)
                        sheet.write(y_offset, 13, l['product_qty_adjustment'], format5_1)
                        sheet.write(y_offset, 14, l['product_qty_scrap'], format5_1)
                        end_qty = begin_qty + l['product_qty_in'] - l['product_qty_in_return'] - \
                                  l['product_qty_out'] + l['product_qty_out_return'] + \
                                  l['product_qty_internal'] + l['product_qty_adjustment'] + \
                                  l['product_qty_scrap'] - l['pos_qty'] + l['pos_return_qty']
                        sheet.write(y_offset, 15, end_qty, format5_1)

                        total_begin += begin_qty
                        total_in += l['product_qty_in']
                        total_in_return += l['product_qty_in_return']
                        total_out += l['product_qty_out']
                        total_out_return += l['product_qty_out_return']
                        total_pos += l.get('pos_qty', 0.0)
                        total_pos_return += l.get('pos_return_qty', 0.0)
                        total_int += l['product_qty_internal']
                        total_adj += l['product_qty_adjustment']
                        total_scrap += l['product_qty_scrap']
                        total_end_qty += end_qty

                        y_offset += 1
                        i += 1
                    y_offset += 1
                    print("location name.......",location_name.display_name)
                    sheet.write(y_offset, 0, location_name.display_name, format5)
                    sheet.write(y_offset, 1, "", format5)
                    sheet.write(y_offset, 2, '', format5)
                    sheet.write(y_offset, 3, '', format5)
                    sheet.write(y_offset, 4, 'Total', format5)
                    sheet.write(y_offset, 5, total_begin, format5_border_top)
                    sheet.write(y_offset, 6, total_in, format5_border_top)
                    sheet.write(y_offset, 7, total_in_return, format5_border_top)
                    sheet.write(y_offset, 8, total_out, format5_border_top)
                    sheet.write(y_offset, 9, total_out_return, format5_border_top)
                    sheet.write(y_offset, 10, total_pos, format5_border_top)
                    sheet.write(y_offset, 11, total_pos_return, format5_border_top)
                    sheet.write(y_offset, 12, total_int, format5_border_top)
                    sheet.write(y_offset, 13, total_adj, format5_border_top)
                    sheet.write(y_offset, 14, total_scrap, format5_border_top)
                    sheet.write(y_offset, 15, total_end_qty, format5_border_top)
                    y_offset += 2

                    grand_total_begin += total_begin
                    grand_total_in += total_in
                    grand_total_in_return += total_in_return
                    grand_total_out += total_out
                    grand_total_out_return += total_out_return
                    grand_total_pos += total_pos
                    grand_total_pos_return += total_pos_return
                    grand_total_int += total_int
                    grand_total_adj += total_adj
                    grand_total_scrap += total_scrap
                    grand_total_end_qty += total_end_qty

            sheet.write(y_offset, 0, "", format5)
            sheet.write(y_offset, 1, "", format5)
            sheet.write(y_offset, 2, "", format5)
            sheet.write(y_offset, 3, "", format5)
            sheet.write(y_offset, 4, "Total Inventory", format5)
            sheet.write(y_offset, 5, grand_total_begin, format5)
            sheet.write(y_offset, 6, grand_total_in, format5)
            sheet.write(y_offset, 7, grand_total_in_return, format5)
            sheet.write(y_offset, 8, grand_total_out, format5)
            sheet.write(y_offset, 9, grand_total_out_return, format5)
            sheet.write(y_offset, 10, grand_total_pos, format5)
            sheet.write(y_offset, 11, grand_total_pos_return, format5)
            sheet.write(y_offset, 12, grand_total_int, format5)
            sheet.write(y_offset, 13, grand_total_adj, format5)
            sheet.write(y_offset, 14, grand_total_scrap, format5)
            sheet.write(y_offset, 15, grand_total_end_qty, format5)
            y_offset += 1
        else:
            report_obj = self.env['report.stock_inventory_excel_report.stock_report_by_category']
            lines = report_obj._get_lines_xls(data, company.id)

            grand_total_begin = 0.0
            grand_total_in = 0.0
            grand_total_in_return = 0.0
            grand_total_out = 0.0
            grand_total_out_return = 0.0
            grand_total_pos = 0.0
            grand_total_pos_return = 0.0
            grand_total_int = 0.0
            grand_total_adj = 0.0
            grand_total_scrap = 0.0
            grand_total_end_qty = 0.0

            y_offset = 10
            for categ in lines.items():
                sheet.write(y_offset, 0, report_obj._get_categ(categ[0]), format5_2)
                y_offset += 1
                i = 1

                total_begin = 0.0
                total_in = 0.0
                total_in_return = 0.0
                total_out = 0.0
                total_out_return = 0.0
                total_pos = 0.0
                total_pos_return = 0.0
                total_int = 0.0
                total_adj = 0.0
                total_scrap = 0.0
                total_end_qty = 0.0

                for l in categ[1]:
                    product = product_obj.browse(l['product_id'])
                    sheet.write(y_offset, 0, i, format5_1)

                    prod_name = product.name_get()[0][1]
                    sheet.write(y_offset, 1, prod_name, format5_1)
                    sheet.write(y_offset, 2, product.default_code or '', format5_1)

                    begin_qty = report_obj._get_beginning_inventory(
                        data, company_id, l['product_id'], l
                    ) or 0.0

                    total_begin += begin_qty
                    sheet.write(y_offset, 3, begin_qty, format5_1)

                    total_in += l['product_qty_in']
                    sheet.write(y_offset, 4, l['product_qty_in'], format5_1)

                    total_in_return += l['product_qty_in_return']
                    sheet.write(y_offset, 5, l['product_qty_in_return'], format5_1)

                    total_out += l['product_qty_out']
                    sheet.write(y_offset, 6, l['product_qty_out'], format5_1)

                    total_out_return += l['product_qty_out_return']
                    sheet.write(y_offset, 7, l['product_qty_out_return'], format5_1)

                    total_pos += l['pos_qty']
                    sheet.write(y_offset, 8, l['pos_qty'], format5_1)

                    total_pos_return += l['pos_return_qty']
                    sheet.write(y_offset, 9, l['pos_return_qty'], format5_1)

                    total_int += l['product_qty_internal']
                    sheet.write(y_offset, 10, l['product_qty_internal'], format5_1)

                    total_adj += l['product_qty_adjustment']
                    sheet.write(y_offset, 11, l['product_qty_adjustment'], format5_1)

                    total_scrap += l['product_qty_scrap']
                    sheet.write(y_offset, 12, l['product_qty_scrap'], format5_1)

                    end_qty = begin_qty + l['product_qty_in'] - l['product_qty_in_return'] - \
                              l['product_qty_out'] + l['product_qty_out_return'] + \
                              l['product_qty_internal'] + l['product_qty_adjustment'] + \
                              l['product_qty_scrap'] + l['pos_return_qty'] - l['pos_qty']
                    total_end_qty += end_qty
                    sheet.write(y_offset, 13, end_qty, format5_1)

                    y_offset += 1
                    i += 1

                sheet.write(y_offset, 0, "", format5)
                sheet.write(y_offset, 1, "", format5)
                sheet.write(y_offset, 2, "", format5)
                sheet.write(y_offset, 3, "", format5)
                sheet.write(y_offset, 4, 'Total', format5)
                sheet.write(y_offset, 5, total_begin, format5_border_top)
                sheet.write(y_offset, 6, total_in, format5_border_top)
                sheet.write(y_offset, 7, total_in_return, format5_border_top)
                sheet.write(y_offset, 8, total_out, format5_border_top)
                sheet.write(y_offset, 9, total_out_return, format5_border_top)
                sheet.write(y_offset, 10, total_pos, format5_border_top)
                sheet.write(y_offset, 11, total_pos_return, format5_border_top)
                sheet.write(y_offset, 12, total_int, format5_border_top)
                sheet.write(y_offset, 13, total_adj, format5_border_top)
                sheet.write(y_offset, 14, total_scrap, format5_border_top)
                sheet.write(y_offset, 15, total_end_qty, format5_border_top)

                grand_total_begin += total_begin
                grand_total_in += total_in
                grand_total_in_return += total_in_return
                grand_total_out += total_out
                grand_total_out_return += total_out_return
                grand_total_pos += total_pos
                grand_total_pos_return += total_pos_return
                grand_total_int += total_int
                grand_total_adj += total_adj
                grand_total_scrap += total_scrap
                grand_total_end_qty += total_end_qty
                y_offset += 1

            y_offset += 1
            sheet.write(y_offset, 0, "", format5)
            sheet.write(y_offset, 1, "", format5)
            sheet.write(y_offset, 2, "", format5)
            sheet.write(y_offset, 3, "", format5)
            sheet.write(y_offset, 4, "Total Inventory", format5)
            sheet.write(y_offset, 5, grand_total_begin, format5)
            sheet.write(y_offset, 6, grand_total_in, format5)
            sheet.write(y_offset, 7, grand_total_in_return, format5)
            sheet.write(y_offset, 8, grand_total_out, format5)
            sheet.write(y_offset, 9, grand_total_out_return, format5)
            sheet.write(y_offset, 10, grand_total_pos, format5)
            sheet.write(y_offset, 11, grand_total_pos_return, format5)
            sheet.write(y_offset, 12, grand_total_int, format5)
            sheet.write(y_offset, 13, grand_total_adj, format5)
            sheet.write(y_offset, 14, grand_total_scrap, format5)
            sheet.write(y_offset, 15, grand_total_end_qty, format5)
            y_offset += 1
