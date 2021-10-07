# -*- coding: utf-8 -*-

import pytz
import time

from operator import itemgetter
from itertools import groupby

from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class inventory_report_category(models.AbstractModel):
    _name = 'report.stock_inventory_excel_report.stock_report_by_category'
    _description = 'Stock Report By Category'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.begining_qty = 0.0
        self.total_in = 0.0
        self.total_out = 0.0
        self.total_int = 0.0
        self.total_adj = 0.0
        self.total_begin = 0.0
        self.total_end = 0.0
        self.total_scrap = 0.0
        self.total_inventory = []
        self.value_exist = {}
        return {
            'doc_ids': self._ids,
            'docs': self,
            'data': data,
            'time': time,
            'get_warehouse_name': self.get_warehouse_name,
            'get_company': self._get_company,
            'get_product_name': self._product_name,
            'get_categ': self._get_categ,
            'get_lines': self._get_lines,
            'get_beginning_inventory': self._get_beginning_inventory,
            'get_ending_inventory': self._get_ending_inventory,
            # 'get_scrap_inventory': self._get_scrap_inventory,
            # 'get_scrap_quantity': self._get_scrap_quantity,
            'get_value_exist': self._get_value_exist,
            'total_in': self._total_in,
            'total_out': self._total_out,
            'total_int': self._total_int,
            'total_adj': self._total_adj,
            'total_begin': self._total_begin,
            'total_vals': self._total_vals,
            'total_end': self._total_end,
            'total_scrap': self._total_scrap,
            # 'total_scrap_val':self._total_scrap_val,
            }

    def _total_in(self):
        """
        category wise inward Qty
        """
        return self.total_in

    def _total_out(self):
        """
        category wise out Qty
        """
        return self.total_out

    def _total_int(self):
        """
        category wise internal Qty
        """
        return self.total_int

    def _total_adj(self):
        """
        category wise adjustment Qty
        """
        return self.total_adj

    def _total_begin(self):
        """
        category wise begining Qty
        """
        return self.total_begin

    def _total_end(self):
        """
        category wise ending Qty
        """
        return self.total_end

    def _total_scrap(self):
        """
        Warehouse wise Scrap Qty
        """
        return self.total_scrap

    # def _total_scrap_val(self):
    #     """
    #     Warehouse wise Total Scrap Qty
    #     """
    #     return self.total_scrap_val

    def _total_vals(self, company_id):
        """
        Grand Total Inventory
        """
        ftotal_in = ftotal_out = ftotal_int = ftotal_adj = ftotal_begin = ftotal_end = ftotal_scrap = 0.0
        for data in self.total_inventory:
            for key,value in data.items():
                if key[1] == company_id:
                    ftotal_in += value['total_in']
                    ftotal_out += value['total_out']
                    ftotal_int += value['total_int']
                    ftotal_adj += value['total_adj']
                    ftotal_begin += value['total_begin']
                    ftotal_scrap += value['total_scrap']
                    ftotal_end += value['total_end']

        return ftotal_begin, ftotal_in,ftotal_out,ftotal_int,ftotal_adj,ftotal_scrap,ftotal_end 

    def _get_value_exist(self,categ_id, company_id):
        """
        Compute Total Values
        """
        total_in = total_out = total_int = total_adj = total_begin  = total_scrap = 0.0
        for warehouse in self.value_exist[categ_id]:
            total_in  += warehouse.get('product_qty_in',0.0)
            total_out  += warehouse.get('product_qty_out',0.0)
            total_int  += warehouse.get('product_qty_internal',0.0)
            total_adj  += warehouse.get('product_qty_adjustment',0.0)
            total_begin += warehouse.get('begining_qty',0.0)
            total_scrap += warehouse.get('product_qty_scrap',0.0)
        self.total_in = total_in
        self.total_out = total_out
        self.total_int = total_int
        self.total_adj = total_adj
        self.total_begin = total_begin
        self.total_scrap = total_scrap
        self.total_end = total_begin + total_in + total_out + total_int + total_adj + total_scrap
        self.total_inventory.append({
                                     (categ_id,company_id):{
                                                            'total_in': total_in, 
                                                            'total_out': total_out,
                                                            'total_int':total_int,
                                                            'total_adj':total_adj,
                                                            'total_begin':total_begin,
                                                            'total_scrap':total_scrap,
                                                            'total_end':total_begin + total_in + total_out + total_int + total_adj + total_scrap,
                                                            }})
        return ''

    def _get_company(self, company_ids):
        res_company_pool = self.env['res.company']
        if not company_ids:
            company_ids  = [x.id for x in res_company_pool.search([])]

        #filter to only have warehouses.
        selected_companies = []
        for company_id in company_ids:
            if self.env['stock.warehouse'].search([('company_id','=',company_id)]):
                selected_companies.append(company_id)

        return res_company_pool.browse(selected_companies).read(['name'])

    def get_warehouse_name(self, warehouse_ids):
        """
        Return warehouse names
            - WH A, WH B...
        """
        warehouse_obj = self.env['stock.warehouse']
        if not warehouse_ids:
            warehouse_ids = [x.id for x in warehouse_obj.search([])]
        war_detail = warehouse_obj.read(warehouse_ids,['name'])
        return ', '.join([lt['name'] or '' for lt in war_detail])

    def _get_beginning_inventory(self, data, company_id,product_id,current_record):
        """
        Process:
            -Pass locations , start date and product_id
        Return:
            - Beginning inventory of product for exact date
        """

        #find all warehouses and get data for that product
        warehouse_ids = data['form'] and data['form'].get('warehouse_ids',[]) or []
        if not warehouse_ids:
            warehouse_ids = self.find_warehouses(company_id)
        #find all locations from all warehouse for that company

        location_id = data['form'] and data['form'].get('location_id') or False
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_ids)

        from_date = self.convert_withtimezone(data['form']['start_date']+' 00:00:00')
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
                            WHERE p.scheduled_date <  %s AND (m.location_id in %s) AND m.state='done' AND pp.active=True AND pp.id = %s
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
                            WHERE p.scheduled_date <  %s AND (m.location_dest_id in %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                            GROUP BY  pp.id,pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                            ))
                        AS foo
                        GROUP BY id
                    ''',(from_date, tuple(locations),product_id, from_date, tuple(locations),product_id))

        res = self._cr.dictfetchall()
        self.begining_qty = res and res[0].get('qty',0.0) or 0.0

        current_record.update({'begining_qty': res and res[0].get('qty',0.0) or 0.0})
        return self.begining_qty

    def _get_ending_inventory(self, in_qty, out_qty,internal_qty,adjust_qty,scrap_qty):
        """
        Process:
            -Inward, outward, internal, adjustment
        Return:
            - total of those qty
        """
        return self.begining_qty + in_qty + out_qty + internal_qty + adjust_qty + scrap_qty

    def _remove_zero_inventory(self, values):
        final_values = []
        for rm_zero in values:
            if rm_zero['product_qty_in'] == 0.0 and rm_zero['product_qty_internal'] == 0.0 and rm_zero['product_qty_out'] == 0.0 and rm_zero['product_qty_adjustment'] == 0.0:
                pass
            else: final_values.append(rm_zero)
        return final_values

    def _remove_product_cate_ids(self, values, filter_product_categ_ids):
        final_values = []
        for rm_products in values:
            if rm_products['categ_id'] not in filter_product_categ_ids:
                pass
            else: final_values.append(rm_products)
        return final_values

    def _get_categ(self, categ):
        """
        Find category name with id
        """
        return self.env['product.category'].browse(categ).display_name

    def _product_name(self, product_id):
        """
        Find product name and assign to it
        """
        product = self.env['product.product'].browse(product_id).name_get()
        return product and product[0] and product[0][1] or ''

    def find_warehouses(self,company_id):
        """
        Find all warehouses
        """
        return [x.id for x in self.env['stock.warehouse'].search([('company_id','=',company_id)])]

    def _find_locations(self, warehouses):
        """
            Find all warehouses stock locations and its childs.
        """
        warehouse_obj = self.env['stock.warehouse']
        location_obj = self.env['stock.location']
        stock_ids = []
        for warehouse in warehouses:
            stock_ids.append(warehouse_obj.sudo().browse(warehouse).view_location_id.id)
        #stock_ids = [x['view_location_id'] and x['view_location_id'][0] for x in warehouse_obj.sudo().read(self.cr, 1, warehouses, ['view_location_id'])]
        return [l.id for l in location_obj.search([('location_id', 'child_of', stock_ids)])]

    def convert_withtimezone(self, userdate):
        """ 
        Convert to Time-Zone with compare to UTC
        """
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

    def category_wise_value_xls(self,
            start_date, end_date, locations,
            include_zero=False, filter_product_categ_ids=[]
        ):
        self._cr.execute('''
            SELECT pp.id AS product_id,pt.categ_id,
                sum((
                CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.sale_line_id is not null AND sp.scheduled_date >= %s and sp.scheduled_date<= %s 
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS product_qty_out,

                sum((
                CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory'  AND sm.sale_line_id is not null AND sp.scheduled_date >= %s and sp.scheduled_date<= %s
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS product_qty_out_return,
            
                sum((
                CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sp.scheduled_date >= %s and sp.scheduled_date<= %s
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS pos_qty,

                sum((
                CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.purchase_line_id is not null  AND sp.scheduled_date >= %s and sp.scheduled_date<= %s
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS product_qty_in,

                sum((
                CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.purchase_line_id is not null AND sp.scheduled_date >= %s and sp.scheduled_date<= %s
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS product_qty_in_return,

                sum((
                CASE WHEN spt.code in ('outgoing') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' AND sp.scheduled_date >= %s and sp.scheduled_date<= %s  
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS pos_return_qty,

                sum((
                CASE WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                THEN (sm.product_qty * pu.factor / pu2.factor)  
                WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                THEN (sm.product_qty * pu.factor / pu2.factor) 
                ELSE 0.0 
                END
                )) AS product_qty_internal,
            
                sum((
                CASE WHEN sourcel.usage = 'inventory' AND sm.scrapped = false AND sm.location_dest_id in %s  
                THEN  (sm.product_qty * pu.factor / pu2.factor)
                WHEN destl.usage ='inventory' AND sm.scrapped = false AND sm.location_id in %s 
                THEN -(sm.product_qty * pu.factor / pu2.factor)
                ELSE 0.0 
                END
                )) AS product_qty_adjustment,
                sum((
                CASE WHEN sm.scrapped=true
                THEN  -(ss.scrap_qty * pu.factor / pu2.factor)
                ELSE 0.0 
                END
                )) AS product_qty_scrap
            
            FROM product_product pp 
            LEFT JOIN  stock_move sm ON (sm.product_id = pp.id and sm.date >= %s and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
            LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
            LEFT JOIN stock_picking_type spt ON (spt.id=sp.picking_type_id)
            LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
            LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
            LEFT JOIN uom_uom pu ON (sm.product_uom=pu.id)
            LEFT JOIN uom_uom pu2 ON (sm.product_uom=pu2.id)
            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
            LEFT JOIN stock_scrap ss ON (ss.product_id = sm.product_id)
            GROUP BY pt.categ_id, pp.id order by pt.categ_id ''',(
                tuple(locations),start_date, end_date,
                tuple(locations),start_date, end_date,
                tuple(locations),start_date, end_date,
                tuple(locations),start_date, end_date,
                tuple(locations),start_date, end_date,
                tuple(locations),start_date, end_date,
                tuple(locations),tuple(locations),tuple(locations),
                tuple(locations), start_date, end_date
            )
        )

        values = self._cr.dictfetchall()

        for none_to_update in values:
            if not none_to_update.get('product_qty_out'):
                none_to_update.update({'product_qty_out':0.0})
            if not none_to_update.get('product_qty_in'):
                none_to_update.update({'product_qty_in':0.0})

        #Removed zero values dictionaries
        if not include_zero:
            values = self._remove_zero_inventory(values)
        #filter by categories
        if filter_product_categ_ids:
            values = self._remove_product_cate_ids(values, filter_product_categ_ids)
        return values

    def _get_lines_xls(self, data, company):
        form = data['form']
 
        start_date = self.convert_withtimezone(
            form['start_date']+' 00:00:00'
        )
        end_date =  self.convert_withtimezone(
            form['end_date']+' 23:59:59'
        )
 
        warehouse_ids = form.get('warehouse_ids',[])
        include_zero = form.get('include_zero', False)
        filter_product_categ_ids = form.get('filter_product_categ_ids', [])

        if not warehouse_ids:
            warehouse_ids = self.find_warehouses(company)
 
        #find all locations from all warehouse for that company
        location_id = form.get('location_id') or False
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_ids)
 
        #get data from all warehouses.
        records = self.category_wise_value_xls(
            start_date, end_date, locations,
            include_zero, filter_product_categ_ids
        )
 
        #records by categories
        sort_by_categories = sorted(
            records, key=itemgetter('categ_id')
        )
        records_by_categories = dict(
            (k, [v for v in itr])
            for k, itr in groupby(
                sort_by_categories, itemgetter('categ_id')
            )
        )
 
        self.value_exist = records_by_categories
        return records_by_categories

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
