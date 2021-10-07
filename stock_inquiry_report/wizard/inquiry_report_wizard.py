 # -*- coding: utf-8 -*-
import base64
from datetime import datetime
import io
import time
from dateutil import relativedelta
import xlwt

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInquiryReportWizard(models.TransientModel):

    _name = 'stock.inquiry.report.wizard'
    _description = 'Stock Inquiry Report Wizard'

    _rec_name = "location_id"

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Warehouses",
        required=False
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True,
    )
    product_categ_id = fields.Many2one(
        'product.category',
        string="Product Category",
        required=True,
    )
    date_start = fields.Date(
        string="From Date",
        required=False
    )
    date_end = fields.Date(
        string="To Date",
        required=False
    )
    location_id = fields.Many2one(
        'stock.location',
        string="Location",
        required=True,
    )
    line_ids = fields.One2many(
        'stock.inquiry.report.wizard.lines',
        'wizard_id',
        string="Lines",
        readonly=True
    )
    in_total= fields.Float("In Total",readonly=True,compute='compute_total',default= 0.0)
    out_total = fields.Float("Out Total",readonly=True,compute='compute_total',default= 0.0)

    style2_title = xlwt.easyxf(
        'font: name Times New Roman, bold on;align: horiz  left;',
        num_format_str='MM/DD/YYYY'
    )
    style2_title_value = xlwt.easyxf(
        'font: name Times New Roman bold on;align: horiz  left;',
        num_format_str='MM/DD/YYYY'
    )
    style2_date = xlwt.easyxf(
        'font: name Times New Roman bold on;align: horiz  right;\
        borders: top thin, bottom thin, left thin, right thin;',
        num_format_str='MM/DD/YYYY'
    )
    table_data_right = xlwt.easyxf(
        'font: name Times New Roman bold on;align: horiz  right;\
        borders: top thin, bottom thin, left thin, right thin;',
        num_format_str='#,##0'
    )
    table_data_left = xlwt.easyxf(
        'font: name Times New Roman bold on;align: horiz left;\
        borders: top thin, bottom thin, left thin, right thin;',
        num_format_str='#,##0'
    )
    table_title = xlwt.easyxf(
        'font: name Times New Roman, bold on;\
        borders: top thin, bottom thin, left thin, right thin;',
        num_format_str='#,##0.00'
    )
    table_title_right = xlwt.easyxf(
        'font: name Times New Roman, bold on; align: horiz right;\
        borders: top thin, bottom thin, left thin, right thin;',
        num_format_str='#,##0.00'
    )

    @api.onchange('product_id')
    def onchange_product(self):
        self.product_categ_id = self.product_id.categ_id

    def compute_total(self):
        tmp_in_total = 0.0
        tmp_out_total = 0.0
        if self.line_ids:
            for line in self.line_ids:
                tmp_in_total += line.in_qty
                tmp_out_total += line.out_qty
        self.in_total = tmp_in_total
        self.out_total = tmp_out_total

    def action_compute_lines(self):
        self.line_ids = [(6,  0, [])]

        if self.warehouse_id:
            if self.date_start:
                self._cr.execute("""
                    SELECT
                        move.id,
                        move.product_qty,
                        0.0 as sale_price,
                        move.sale_line_id,
                        0.0 as cost_price,
                        0.0 as amount,
                        move.reference as reference,
                        move.origin as description,
                        move.price_unit as price_unit,
                        respartner.name as partner_id,
                        move.date,
                        0 as balance,
                        spt.code,
                        CASE
                            WHEN move.location_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS out_qty,
                        CASE
                            WHEN move.location_dest_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS in_qty
                    FROM
                        stock_move move
                        LEFT JOIN stock_picking_type spt ON (spt.id=move.picking_type_id)
                        LEFT JOIN res_partner respartner ON (respartner.id=move.partner_id)
                    WHERE
                        move.date::date >= %s AND
                        move.date::date <= %s AND
                        (move.location_id = %s OR
                        move.location_dest_id = %s) AND
                        move.product_id = %s AND
                        move.warehouse_id=%s AND
                        move.state = 'done'
                    ORDER BY
                        move.date
                """, (self.location_id.id,
                      self.location_id.id,
                      self.date_start,
                      self.date_end,
                      self.location_id.id,
                      self.location_id.id,
                      self.product_id.id,
                      self.warehouse_id.id)
                )
            else:
                self._cr.execute("""
                    SELECT
                        move.id,
                        move.product_qty,
                        0.0 as sale_price,
                        move.sale_line_id,
                        0.0 as cost_price,
                        0.0 as amount,
                        move.reference as reference,
                        move.origin as description,
                        move.price_unit as price_unit,
                        respartner.name as partner_id,
                        move.date,
                        0 as balance,
                        spt.code,
                        CASE
                            WHEN move.location_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS out_qty,
                        CASE
                            WHEN move.location_dest_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS in_qty
                    FROM
                        stock_move move
                        LEFT JOIN stock_picking_type spt ON (spt.id=move.picking_type_id)
                        LEFT JOIN res_partner respartner ON (respartner.id=move.partner_id)
                    WHERE
                        (move.location_id = %s OR
                        move.location_dest_id = %s) AND
                        move.product_id = %s AND
                        move.warehouse_id=%s AND
                        move.state = 'done'
                    ORDER BY
                        move.date
                """, (self.location_id.id,
                      self.location_id.id,
                      self.location_id.id,
                      self.location_id.id,
                      self.product_id.id,
                      self.warehouse_id.id)
                )
        else:
            if self.date_start:
                self._cr.execute("""
                    SELECT
                        move.id,
                        move.product_qty,
                        0.0 as sale_price,
                        move.sale_line_id,
                        0.0 as cost_price,
                        0.0 as amount,
                        move.reference as reference,
                        move.origin as description,
                        move.price_unit as price_unit,
                        respartner.name as partner_id,
                        move.date,
                        0 as balance,
                        move.picking_type_id,
                        spt.code,
                        CASE
                            WHEN move.location_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS out_qty,
                        CASE
                            WHEN move.location_dest_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS in_qty
                    FROM
                        stock_move move
                        LEFT JOIN stock_picking_type spt ON (spt.id=move.picking_type_id)
                        LEFT JOIN res_partner respartner ON (respartner.id=move.partner_id)
                    WHERE
                        move.date::date >= %s AND
                        move.date::date <= %s AND
                        (move.location_id = %s OR
                        move.location_dest_id = %s) AND
                        move.product_id = %s AND
                        move.state = 'done'
                    ORDER BY
                        move.date
                """, (self.location_id.id,
                      self.location_id.id,
                      self.date_start,
                      self.date_end,
                      self.location_id.id,
                      self.location_id.id,
                      self.product_id.id)
                )
            else:
                self._cr.execute("""
                    SELECT
                        move.id,
                        move.product_qty,
                        0.0 as sale_price,
                        move.sale_line_id,
                        0.0 as cost_price,
                        0.0 as amount,
                        move.reference as reference,
                        move.origin as description,
                        move.price_unit as price_unit,
                        respartner.name as partner_id,
                        move.date,
                        0 as balance,
                        move.picking_type_id,
                        spt.code,
                        CASE
                            WHEN move.location_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS out_qty,
                        CASE
                            WHEN move.location_dest_id = %s
                            THEN move.product_qty
                            ELSE 0.0
                        END AS in_qty
                    FROM
                        stock_move move
                        LEFT JOIN stock_picking_type spt ON (spt.id=move.picking_type_id)
                        LEFT JOIN res_partner respartner ON (respartner.id=move.partner_id)
                    WHERE
                        (move.location_id = %s OR
                        move.location_dest_id = %s) AND
                        move.product_id = %s AND
                        move.state = 'done'
                    ORDER BY
                        move.date
                """, (self.location_id.id,
                      self.location_id.id,
                      self.location_id.id,
                      self.location_id.id,
                      self.product_id.id)
                )
        move_lines_res = self._cr.dictfetchall()

        if self.date_start:
            self._cr.execute(''' 
                SELECT id,coalesce(sum(qty), 0.0) as qty
                FROM
                    ((
                    SELECT pp.id, pp.default_code,m.date,
                        CASE when pt.uom_id = m.product_uom 
                        THEN u.name 
                        ELSE (select name from uom_uom where id = pt.uom_id) 
                        END AS name,
                
                        CASE when pt.uom_id = m.product_uom  
                        THEN coalesce(sum(-m.product_qty)::decimal, 0.0)
                        ELSE coalesce(sum(-m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                        END AS qty
                
                    FROM product_product pp 
                    LEFT JOIN stock_move m ON (m.product_id=pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN stock_location l ON (m.location_id=l.id)    
                    LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                    LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN uom_uom u ON (m.product_uom=u.id)
                    WHERE p.scheduled_date <  %s AND (m.location_id = %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                    GROUP BY  pp.id, pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                    ) 
                    UNION ALL
                    (
                    SELECT pp.id, pp.default_code,m.date,
                        CASE when pt.uom_id = m.product_uom 
                        THEN u.name 
                        ELSE (select name from uom_uom where id = pt.uom_id) 
                        END AS name,
                
                        CASE when pt.uom_id = m.product_uom 
                        THEN coalesce(sum(m.product_qty)::decimal, 0.0)
                        ELSE coalesce(sum(m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                        END  AS qty
                    FROM product_product pp 
                    LEFT JOIN stock_move m ON (m.product_id=pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN stock_location l ON (m.location_dest_id=l.id)    
                    LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                    LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN uom_uom u ON (m.product_uom=u.id)
                    WHERE p.scheduled_date <  %s AND (m.location_dest_id = %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                    GROUP BY  pp.id,pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                    ))
                AS foo
                GROUP BY id
            ''',(self.date_start, self.location_id.id,self.product_id.id,
                 self.date_start, self.location_id.id,self.product_id.id))

            res = self._cr.dictfetchall()
        else:
            self._cr.execute(''' 
                SELECT id,coalesce(sum(qty), 0.0) as qty
                FROM
                    ((
                    SELECT pp.id, pp.default_code,m.date,
                        CASE when pt.uom_id = m.product_uom 
                        THEN u.name 
                        ELSE (select name from uom_uom where id = pt.uom_id) 
                        END AS name,
                
                        CASE when pt.uom_id = m.product_uom  
                        THEN coalesce(sum(-m.product_qty)::decimal, 0.0)
                        ELSE coalesce(sum(-m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                        END AS qty
                
                    FROM product_product pp 
                    LEFT JOIN stock_move m ON (m.product_id=pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN stock_location l ON (m.location_id=l.id)    
                    LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                    LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN uom_uom u ON (m.product_uom=u.id)
                    WHERE (m.location_id = %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                    GROUP BY  pp.id, pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                    ) 
                    UNION ALL
                    (
                    SELECT pp.id, pp.default_code,m.date,
                        CASE when pt.uom_id = m.product_uom 
                        THEN u.name 
                        ELSE (select name from uom_uom where id = pt.uom_id) 
                        END AS name,
                
                        CASE when pt.uom_id = m.product_uom 
                        THEN coalesce(sum(m.product_qty)::decimal, 0.0)
                        ELSE coalesce(sum(m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                        END  AS qty
                    FROM product_product pp 
                    LEFT JOIN stock_move m ON (m.product_id=pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN stock_location l ON (m.location_dest_id=l.id)    
                    LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                    LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN uom_uom u ON (m.product_uom=u.id)
                    WHERE (m.location_dest_id = %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                    GROUP BY  pp.id,pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                    ))
                AS foo
                GROUP BY id
            ''',(self.location_id.id,self.product_id.id,
                 self.location_id.id,self.product_id.id))

            res = self._cr.dictfetchall()

        begining_qty = res and res[0].get('qty',0.0) or 0.0

        standard_price = self.product_id.price_compute('standard_price')[self.product_id.id]
        list_price = self.product_id.price_compute('list_price')[self.product_id.id]

        for l in move_lines_res:
            print('move', move_lines_res)
            if l.get('in_qty', 0.0) > 0.0:
                begining_qty += l['in_qty']
                l['balance'] = begining_qty
            elif l.get('out_qty', 0.0):
                begining_qty -= l['out_qty']
                l['balance'] = begining_qty

            if l['code'] == 'outgoing':
                if l['sale_line_id']:
                    sale_line = self.env['sale.order.line'].browse(l['sale_line_id'])
                    l['sale_price'] = sale_line.price_unit
                    l['amount'] = l['product_qty'] * sale_line.price_unit
                else:
                    l['sale_price'] = list_price
                    l['amount'] = l['product_qty'] * list_price
            else:
                l['cost_price'] = standard_price
                # l['amount'] = qty * standard_price

            if l['code'] is not None and l['code'] == 'outgoing':
                l['price_unit'] = 0.0
            elif l['code'] is not None and l['code'] == 'internal':
                l['price_unit'] = 0.0
            else:
                price = l['price_unit'] or 0.0
                qty = l['product_qty'] or 0.0
                l['price_unit'] = price
                l['amount'] = qty * price
            del l['sale_line_id']

            #
            # price_unit = l.get('price_unit', 0.0)
            # if price_unit is None:
            #     price_unit = 0.0
            #
            # if price_unit > 0.0:
            #     l.update({
            #         'cost_price': price_unit,
            #         'sale_price': 0.0,
            #         'amount': l['in_qty'] * price_unit
            #     })
            # else:
            #     l.update({
            #         'sale_price': -1.0 * price_unit,
            #         'cost_price': 0.0,
            #         'amount': -1 * l['out_qty'] * price_unit
            #     })
        
        lines = [(0, 0, l) for l in move_lines_res]
        self.line_ids = lines

    def action_export_excel(self):
        self.action_compute_lines()

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Stock Inquiry')

        row_count = 0
        sheet.write(row_count, 0, "Company", self.style2_title)
        sheet.write(row_count, 1, self.company_id.display_name or '', self.style2_title_value)

        row_count += 1
        sheet.write(row_count, 0, "Product", self.style2_title)
        sheet.write(row_count, 1, self.product_id.display_name or '', self.style2_title_value)
        sheet.write(row_count, 5, "Date From", self.style2_title)
        sheet.write(row_count, 6, self.date_start or '', self.style2_title_value)

        row_count += 1
        sheet.write(row_count, 0, "Product Category", self.style2_title)
        sheet.write(row_count, 1, self.product_categ_id.display_name or '', self.style2_title_value)
        sheet.write(row_count, 5, "To Date", self.style2_title)
        sheet.write(row_count, 6, self.date_end or '', self.style2_title_value)

        row_count += 1
        sheet.write(row_count, 0, "Warehouse", self.style2_title)
        sheet.write(row_count, 1, self.warehouse_id.display_name or '', self.style2_title_value)
        sheet.write(row_count, 5, "Location", self.style2_title)
        sheet.write(row_count, 6, self.location_id.display_name or '', self.style2_title_value)

        row_count += 2

        # Table Header
        sheet.write(
            row_count, 0,
            "#", self.table_title
        )
        sheet.write(
            row_count, 1,
            "Date", self.table_title_right
        )
        sheet.write(
            row_count, 2,
            "Stock Picking No", self.table_title
        )
        sheet.write(
            row_count, 3,
            "Source Doc", self.table_title
        )
        sheet.write(
            row_count, 4,
            "Name", self.table_title
        )
        sheet.write(
            row_count, 5,
            "IN", self.table_title_right
        )
        sheet.write(
            row_count, 6,
            "OUT", self.table_title_right
        )
        sheet.write(
            row_count, 7,
            "BALANCE", self.table_title_right
        )
        # sheet.write(
        #     row_count, 8,
        #     "COST PRICE", self.table_title_right
        # )
        sheet.write(
            row_count, 8,
            "PURCHASE PRICE", self.table_title_right
        )
        sheet.write(
            row_count, 9,
            "SALE PRICE", self.table_title_right
        )
        sheet.write(
            row_count, 10,
            "AMOUNT", self.table_title_right
        )

        # table values
        row_count += 1
        count = 1
        for line in self.line_ids:
            sheet.write(
                row_count, 0,
                count, self.table_data_left
            )
            count += 1
            sheet.write(
                row_count, 1,
                line.date,
                self.style2_date
            )
            sheet.write(
                row_count, 2,
                line.reference,
                self.table_data_left
            )
            sheet.write(
                row_count, 3,
                line.description or '',
                self.table_data_left
            )
            sheet.write(
                row_count,4,
                line.description or '',
                self.table_data_left)
            sheet.write(
                row_count, 5,
                line.in_qty,
                self.table_data_right
            )
            sheet.write(
                row_count, 6,
                line.out_qty,
                self.table_data_right
            )
            sheet.write(
                row_count, 7,
                line.balance,
                self.table_data_right
            )
            # sheet.write(
            #     row_count, 8,
            #     line.cost_price,
            #     self.table_data_right
            # )

            sheet.write(
                row_count, 8,
                line.price_unit,
                self.table_data_right
            )
            sheet.write(
                row_count, 9,
                line.sale_price,
                self.table_data_right
            )
            sheet.write(
                row_count, 10,
                line.amount,
                self.table_data_right
            )

            row_count += 1

        sheet.write(
                row_count, 4,
                "TOTAL",
                self.table_title
            )
        sheet.write(
                row_count, 5,
                self.in_total,
                self.table_data_right
            )
        sheet.write(
                row_count, 6,
                self.out_total,
                self.table_data_right
            )
        stream = io.BytesIO()

        workbook.save(stream)
        attach_id = self.env['stock.inquiry.excel.output'].create({
            'name': str(self.date_start) + '.xls',
            'filename': base64.encodestring(
                stream.getvalue()
            )
        })
        return {
            'type': 'ir.actions.act_window',
            'name': ('Report'),
            'res_model': 'stock.inquiry.excel.output',
            'res_id': attach_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }


class StockInquiryReportWizardLines(models.TransientModel):
    _name = 'stock.inquiry.report.wizard.lines'
    _description = 'Stock Inquiry Report Wizard Lines'

    date = fields.Datetime(
        string="Date"
    )
    reference = fields.Char(
        string="Stock Picking No"
    )
    product_qty = fields.Float('Product Qty')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking')
    code = fields.Char()
    description = fields.Char(
        string="Source Doc"
    )
    partner_id = fields.Char(
        string="Name"
    )
    in_qty = fields.Float(
        string="IN"
    )
    out_qty = fields.Float(
        string="OUT"
    )
    balance = fields.Float(
        string="BALANCE"
    )
    cost_price = fields.Float(
        string="COST PRICE"
    )
    sale_price = fields.Float(
        string="SALE PRICE"
    )
    amount = fields.Float(
        string="AMOUNT"
    )
    price_unit = fields.Float(string="PURCHASE PRICE")
    wizard_id = fields.Many2one(
        'stock.inquiry.report.wizard',
        string="Wizard"
    )


class Output(models.TransientModel):
    _name = 'stock.inquiry.excel.output'
    _description = 'Excel Report Output'

    name = fields.Char(
        string='File Name',
        size=256,
        readonly=True
    )
    filename = fields.Binary(
        string='File to Download',
        readonly=True
    )

