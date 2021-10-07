from odoo import models, fields, api,_
from io import StringIO
import pytz
import io
import json
import time
import xlsxwriter
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class inventory_report(models.AbstractModel):
    _name = 'report.inventory_reorder_report.inventory_report_excel'
    _description = 'Inventory Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.begining_qty = 0.0
        self.total_in = 0.0
        self.total_out = 0.0
        self.total_int = 0.0
        self.total_adj = 0.0
        self.total_begin = 0.0
        self.total_end = 0.0
        self.total_inventory = []
        self.value_exist = {}
        return {
            'doc_ids': self._ids,
            'docs': self,
            'data': data,
            'time': time,
            'get_warehouse_name': self.get_warehouse_name,
            'get_product_name': self._product_name,
            'get_default_code': self._product_code,
            'get_warehouse': self._get_warehouse,
            'get_lines': self._get_lines,
            'get_beginning_inventory': self._get_beginning_inventory,
            'get_ending_inventory': self._get_ending_inventory,
            'total_in': self._total_in,
            'total_out': self._total_out,
            'total_int': self._total_int,
            'total_adj': self._total_adj,
            'total_begin': self._total_begin,
            'total_end': self._total_end
        }

    def _total_in(self):
        return self.total_in

    def _total_out(self):
        return self.total_out

    def _total_int(self):
        return self.total_int

    def _total_adj(self):
        return self.total_adj

    def _total_begin(self):
        return self.total_begin

    def _total_end(self):
        return self.total_end

    def get_warehouse_name(self, warehouse_ids):
        warehouse_obj = self.env['stock.warehouse']
        if not warehouse_ids:
            warehouse_ids = [x.id for x in warehouse_obj.search([])]
        war_detail = warehouse_obj.read(warehouse_ids, ['name'])
        return ', '.join([lt['name'] or '' for lt in war_detail])

    # Added conversion with dual uom #need to check in deeply
    def _get_beginning_inventory(self, data, warehouse_id, product_id, current_record):
        location_id = data['form'] and data['form'].get('location_id') or False
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_id)
        from_date = self.convert_withtimezone(data['form']['start_date'] + ' 00:00:00')
        self._cr.execute(''' 
                            SELECT id,coalesce(sum(qty), 0.0) AS qty
                            FROM
                                ((
                                SELECT
                                    pp.id, pp.default_code,m.date,
                                    CASE WHEN pt.uom_id = m.product_uom 
                                    THEN u.name 
                                    ELSE (select name from product_uom where id = pt.uom_id) end AS name,

                                    CASE WHEN pt.uom_id = m.product_uom  
                                    THEN coalesce(sum(-m.product_qty)::decimal, 0.0)
                                    ELSE coalesce(sum(-m.product_qty * pu.factor / u.factor )::decimal, 0.0) END  AS qty

                                FROM product_product pp 
                                LEFT JOIN stock_move m ON (m.product_id=pp.id)
                                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                                LEFT JOIN stock_location l on(m.location_id=l.id)
                                LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                                LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                                LEFT JOIN uom_uom u ON (m.product_uom=u.id)

                                WHERE m.date <  %s AND (m.location_id in %s) 
                                AND m.state='done' and pp.active=True AND pp.id = %s
                                GROUP BY  pp.id,pt.uom_id , m.product_uom ,
                                pp.default_code,u.name,m.date
                                ) 
                                UNION ALL
                                (
                                SELECT
                                    pp.id, pp.default_code,m.date,
                                    CASE WHEN pt.uom_id = m.product_uom 
                                    THEN u.name 
                                    ELSE (select name from product_uom where id = pt.uom_id) end AS name,

                                    CASE WHEN pt.uom_id = m.product_uom 
                                    THEN coalesce(sum(m.product_qty)::decimal, 0.0)
                                    ELSE coalesce(sum(m.product_qty * pu.factor / u.factor )::decimal, 0.0) END  AS qty
                                FROM product_product pp 
                                LEFT JOIN stock_move m ON (m.product_id=pp.id)
                                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                                LEFT JOIN stock_location l on(m.location_dest_id=l.id)    
                                LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                                LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                                LEFT JOIN uom_uom u ON (m.product_uom=u.id)

                                WHERE m.date <  %s AND (m.location_dest_id in %s) 
                                AND m.state='done' and pp.active=True AND pp.id = %s
                                GROUP BY  pp.id,pt.uom_id , m.product_uom ,
                                pp.default_code,u.name,m.date
                                ))
                                AS foo
                            group BY id
                            ''', (from_date, tuple(locations), product_id, from_date, tuple(locations), product_id))

        res = self._cr.dictfetchall()
        self.begining_qty = res and res[0].get('qty', 0.0) or 0.0
        current_record.update({'begining_qty': res and res[0].get('qty', 0.0) or 0.0})
        return self.begining_qty

    def _get_ending_inventory(self, in_qty, out_qty, internal_qty, adjust_qty):
        return round(self.begining_qty + in_qty + out_qty + internal_qty + adjust_qty, 1)

    def convert_withtimezone(self, userdate):
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            # not need if you give default datetime into entry ;)
            user_datetime = user_date  # + relativedelta(hours=24.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def location_wise_value(self, start_date, end_date, locations, include_zero=False, filter_product_ids=[]):
        vals = []
        print("location", locations)
        self._cr.execute('''
                            SELECT pt.name, pp.id AS product_id, pp.default_code,
                                sum((
                                    CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' and destl.usage !='inventory' AND sm.location_id = swo.location_id
                                    THEN -(sm.product_qty * pu.factor / pu2.factor)
                                    ELSE 0.0 
                                    END
                                )) AS product_qty_out,
                                sum((
                                    CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.location_dest_id = swo.location_id
                                    THEN (sm.product_qty * pu.factor / pu2.factor)
                                    ELSE 0.0 
                                    END
                                )) AS product_qty_in,
                                sum((
                                    CASE WHEN (spt.code ='internal' or spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.location_dest_id = swo.location_id
                                    THEN (ROUND((sm.product_qty * pu.factor / pu2.factor),1)) 
                                    WHEN (spt.code='internal' or spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' and destl.usage !='inventory' AND sm.location_dest_id = swo.location_id
                                    THEN -(ROUND((sm.product_qty * pu.factor / pu2.factor),1))
                                    ELSE 0.0 
                                    END
                                )) AS product_qty_internal,

                                sum((
                                    CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s AND sm.location_dest_id = swo.location_id
                                    THEN  (ROUND((sm.product_qty * pu.factor / pu2.factor),1))
                                    WHEN destl.usage ='inventory' AND sm.location_id in %s AND sm.location_dest_id = swo.location_id
                                    THEN -(ROUND((sm.product_qty * pu.factor / pu2.factor),1))
                                    ELSE 0.0 
                                    END
                                )) AS product_qty_adjustment,
                                sum((
                                    CASE WHEN swo.location_id in %s AND sm.location_id IN ('5') AND sm.product_qty >0 AND sm.location_dest_id = swo.location_id
                                    THEN (swo.product_min_qty) 
                                    ELSE 0.0 
                                    END
                                )) AS product_qty_min,
                                sum((
                                    CASE WHEN swo.location_id in %s AND sm.location_id IN ('5') AND sm.product_qty >0 AND swo.location_id = sm.location_dest_id
                                    THEN (swo.product_max_qty)
                                    ELSE 0.0 
                                    END
                                )) AS product_qty_max
                            FROM product_product pp 
                            LEFT JOIN  stock_move sm ON (sm.product_id = pp.id and sm.date >= %s and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                            LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                            LEFT JOIN stock_picking_type spt ON (spt.id=sp.picking_type_id)
                            LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                            LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                            LEFT JOIN uom_uom pu ON (sm.product_uom=pu.id)
                            LEFT JOIN uom_uom pu2 ON (sm.product_uom=pu2.id)
                            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                            LEFT JOIN stock_warehouse_orderpoint swo ON (swo.product_id=pp.id)
                            GROUP BY pp.id, pt.name, pp.default_code
                            order by pp.id
                            ''', (
        tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations),
        tuple(locations), tuple(locations), start_date, end_date))

        values = self._cr.dictfetchall()

        for none_to_update in values:
            if not none_to_update.get('product_qty_out'):
                none_to_update.update({'product_qty_out': 0.0})
            if not none_to_update.get('product_qty_in'):
                none_to_update.update({'product_qty_in': 0.0})

        if not include_zero:
            values = self._remove_zero_inventory(values)

        if filter_product_ids:
            values = self._remove_product_ids(values, filter_product_ids)

        vals.append(values)
        return vals

        # Removed zero values dictionary
        # if not include_zero:
        #     values = self._remove_zero_inventory(values)
        # # filter by products
        # if filter_product_ids:
        #     values = self._remove_product_ids(values, filter_product_ids)
        # return values

    def _remove_zero_inventory(self, values):
        final_values = []
        for rm_zero in values:
            if rm_zero['product_qty_in'] == 0.0 and rm_zero['product_qty_internal'] == 0.0 and rm_zero[
                'product_qty_out'] == 0.0 and rm_zero['product_qty_adjustment'] == 0.0:
                pass
            else:
                final_values.append(rm_zero)
        return final_values

    def _remove_product_ids(self, values, filter_product_ids):
        print("Values=>", values)
        final_values = []
        for rm_products in values:
            if rm_products['product_id'] not in filter_product_ids:
                pass
            else:
                final_values.append(rm_products)
        return final_values

    def _get_warehouse(self, warehouse):
        return self.env['stock.warehouse'].browse(warehouse).read(['name'])[0]['name']

    def _product_name(self, product_id):
        product = self.env['product.product'].browse(product_id).name_get()
        return product and product[0] and product[0][1] or ''

    def _product_code(self, product_id):
        return self.env['product.product'].browse(product_id)['default_code']

    def find_warehouses(self):
        return [x.id for x in self.env['stock.warehouse'].search([])]

    def get_report_name(self):
        return _('Stock Reordering Report')

    def get_report_filename(self, options):
        return self.get_report_name().lower().replace(' ', '_')

    def _find_locations(self, warehouse):
        warehouse_obj = self.env['stock.warehouse']
        location_obj = self.env['stock.location']
        store_location_id = warehouse_obj.browse(warehouse).view_location_id.id
        return [x.id for x in location_obj.search([('location_id', 'child_of', store_location_id)])]

    def _get_lines(self, data):
        start_date = self.convert_withtimezone(data['form']['start_date'] + ' 00:00:00')
        end_date = self.convert_withtimezone(data['form']['end_date'] + ' 23:59:59')

        warehouse_ids = data['form'] and data['form'].get('warehouse_ids', []) or []
        include_zero = data['form'] and data['form'].get('include_zero') or False
        filter_product_ids = data['form'] and data['form'].get('filter_product_ids') or []
        location_id = data['form'] and data['form'].get('location_id') or False
        if not warehouse_ids:
            warehouse_ids = self.find_warehouses()
        final_values = {}
        for warehouse in warehouse_ids:
            # looping for only warehouses which is under current company
            # if self._compare_with_company(warehouse, ):
            locations = self._find_locations(warehouse)
            if location_id:
                if (location_id in locations):
                    final_values.update({
                        warehouse: self.location_wise_value(start_date, end_date, [location_id], include_zero,
                                                            filter_product_ids)
                    })
            else:
                final_values.update({
                    warehouse: self.location_wise_value(start_date, end_date, locations, include_zero,
                                                        filter_product_ids)
                })
        self.value_exist = final_values
        print("Final Value=>", final_values)
        return final_values

    def xlsx_export(self, datas):
        return {
                    'type': 'ir_actions_account_report_download',
                    'data': {'model': 'report.inventory_reorder_report.inventory_report_excel',
                    'options': json.dumps(datas, indent=4, sort_keys=True, default=str),
                    'output_format': 'xlsx',
                    'financial_id': self.env.context.get('id'),
                    }
                }

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        _get_lines = []
        date = None
        warehouse_name = None
        location_name = None
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self.get_report_name())
        fromat0 = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, })
        fromat1 = workbook.add_format({'align': 'center', 'bold': True, 'border': True, })
        fromat2 = workbook.add_format({'align': 'center', 'border': True, })
        fromat3 = workbook.add_format({'align': 'left', 'border': True, })
        fromat4 = workbook.add_format({'align': 'right', 'border': True, })
        sheet.set_column(0, 0, 20)  # Set the first column width to 15
        location_id = options['form'] and options['form'].get('location_id') or False
        if location_id:
            print("Location", location_id)
            location_name = self.env['stock.location'].search([('id', '=', location_id)]).name

        warehouse_id = options['form'] and options['form'].get('warehouse_ids') or False
        if warehouse_id:
            print("Warehouse", warehouse_id)
            warehouse_name = self.env['stock.warehouse'].search([('id', '=', warehouse_id)]).name

        date = (options['form']['start_date']) + ' To ' + (options['form']['end_date'])
        y_offset = 0
        sheet.merge_range(y_offset, 7, y_offset, 10, _('Stock Recording Report'), fromat0)
        y_offset += 2
        sheet.write(y_offset, 0, _('Warehouse Name'), fromat1)
        sheet.write(y_offset, 1, warehouse_name, fromat2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Location Name'), fromat1)
        sheet.write(y_offset, 1, location_name, fromat2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Date'), fromat1)
        sheet.write(y_offset, 1, date, fromat2)
        sheet.set_column(0, 0, 20)
        y_offset += 2
        sheet.write(y_offset, 0, _('Product Name'), fromat1)
        sheet.write(y_offset, 1, _('Internal Reference'), fromat1)
        sheet.write(y_offset, 2, _('Min Qty'), fromat1)
        sheet.write(y_offset, 3, _('Max Qty'), fromat1)
        sheet.write(y_offset, 4, _('On Hand Qty'), fromat1)
        sheet.write(y_offset, 5, _('Over/Reduce Qty'), fromat1)
        sheet.set_column(0, 0, 20)
        lines = self._get_lines(options)
        y_offset += 1
        if lines:
            print("Lines", lines)
            for l in lines:
                print("L", l)
                for loop in lines[l]:
                    print("Loop", loop)
                    for line in loop:
                        sheet.write(y_offset, 0, line['name'], fromat2)
                        sheet.write(y_offset, 1, line['default_code'], fromat2)
                        sheet.write(y_offset, 2, line['product_qty_min'], fromat2)
                        sheet.write(y_offset, 3, line['product_qty_max'], fromat2)
                        sheet.write(y_offset, 4, (line['product_qty_in']+line['product_qty_out']+line['product_qty_internal']+line['product_qty_adjustment']), fromat2)
                        sheet.write(y_offset, 5, ((line['product_qty_in']+line['product_qty_out']+line['product_qty_internal']+line['product_qty_adjustment'])-line['product_qty_max']), fromat2)
                        y_offset += 1
                        print("Line", line)

        workbook.close()
        output.seek(0)
        #response.stream.write(output.read())
        generated_file = output.read()
        output.close()

        return generated_file


