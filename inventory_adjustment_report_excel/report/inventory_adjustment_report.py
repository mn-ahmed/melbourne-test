from io import StringIO
import io
import json
import xlsxwriter
import time
import pytz
from odoo import models, api
import calendar
import copy
import logging
import lxml.html
import xlwt
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter

from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date
from odoo.tools import config
from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval
from odoo.http import controllers_per_module
_logger = logging.getLogger(__name__)

class report_incoming_statement(models.AbstractModel):
    _name = 'report.inventory.adjustment'
    _description = 'Report Inventory Adjustment'
    
    @api.model
    def get_report_values(self, docids, data=None):
        
        return {
            'doc_ids': self._ids,
            'docs': self,
            'data': data,
            'time': time,                      
            } 
    
    def get_report_name(self):
        return _('Inventory Adjustment Report')

    def get_report_filename(self, options):
        """The name that will be used for the file when downloading pdf,xlsx,..."""
        return self.get_report_name().lower().replace(' ', '_')
    
    def get_header_name(self):
        return _('Inventory Adjustment Report')
    
    
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
      
    def get_xlsx(self, options,response=None):        
        output = io.BytesIO()
        get_lines=[]
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self.get_report_name()[:31])
        self._define_formats(workbook)        
        
        y_offset = 0
        df = options['form']['start_date'] if options['form']['start_date'] else u''
        dt = options['form']['end_date'] if options['form']['end_date'] else u''  
        warehouse_id = options['form']['warehouse_id'] if options['form']['warehouse_id'] else u''
        location_id = options['form']['location_id'] if options['form']['location_id'] else u''
        
        sheet.merge_range(y_offset, 3, y_offset, 6, _('Inventory Adjustment Report'), self.format_title)
        y_offset += 2
        
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd','border': True,'align': 'center'})
        number_format = workbook.add_format({'num_format': '#,##0.00','border': True})
        
        sheet.merge_range(y_offset, 0, y_offset, 1, _('Start Date'), self.format_header_center)        
        sheet.set_column(0, 1, 20)  
        sheet.merge_range(y_offset, 2, y_offset, 3, _('End Date'), self.format_header_center)        
        sheet.set_column(2, 3, 20) 
        y_offset += 1              
         
        sheet.merge_range(y_offset, 0, y_offset, 1, df or '', date_format)
        sheet.set_column(0, 1, 20)  
        sheet.merge_range(y_offset, 2, y_offset, 3, dt or '', date_format)
        sheet.set_column(2, 3, 20)               
        y_offset += 2
        
        sheet.write(y_offset, 0, _('No'), self.format_header_center)          
        sheet.write(y_offset, 1, _('Date'), self.format_header_center)  
        sheet.merge_range(y_offset, 2,y_offset, 3, _('Adjustment Name'), self.format_header_center)
        sheet.merge_range(y_offset, 4,y_offset, 6, _('Company'), self.format_header_center)
        sheet.write(y_offset, 7, _('Code'), self.format_header_center)      
        sheet.merge_range(y_offset, 8,y_offset, 10, _('Product '), self.format_header_center)  
        sheet.merge_range(y_offset, 11,y_offset, 13, _('Location '), self.format_header_center)  
        sheet.write(y_offset, 14, _(' Qty'), self.format_header_center)   
        sheet.merge_range(y_offset, 15,y_offset, 17, _('Cost'), self.format_header_center)
        sheet.merge_range(y_offset, 18,y_offset, 20, _('Inventory Gain/Loss'), self.format_header_center)
                          
        y_offset += 1
        user_id = self.env['res.users'].browse(self.env.uid)
        company_id = user_id.company_id
        
        self.env.cr.execute("""select ((si.date at time zone 'utc') at time zone 'asia/rangoon')::date inventory_date,si.name adjustment_name,rc.name company,pt.default_code code,pt.name product,sl.complete_name stock_location,
                                case when sil.theoretical_qty < sil.product_qty then (sil.product_qty-sil.theoretical_qty) 
                                     when sil.theoretical_qty > sil.product_qty then (sil.product_qty-sil.theoretical_qty) 
                                     end as qty,pp.id as product_id                                
                                from stock_move sm,stock_move_line sml,stock_inventory_line sil,stock_inventory si,product_product pp,product_template pt,account_move am,stock_location sl,res_company rc
                                where sm.id=sml.move_id
                                and sm.inventory_id=si.id
                                and sm.product_id=pp.id
                                and pp.product_tmpl_id=pt.id
                                and sil.inventory_id=si.id
                                and sl.id=sil.location_id
                                and rc.id=si.company_id
                                and am.stock_move_id=sm.id
                                and sil.product_id=sml.product_id
                                and sm.inventory_id is not null
                                and si.state not in ('draft','cancel')
                                and ((si.date at time zone 'utc') at time zone 'asia/rangoon')::date between %s and %s
                                and sl.id=%s
                                group by si.name,si.date,rc.name,pt.name,sl.complete_name,pp.id,sil.theoretical_qty,sil.product_qty,pt.default_code                     
                       """,(df,dt,location_id))
        datas = self.env.cr.fetchall()
        row_no = 0
        for record in datas:
            row_no += 1
            sheet.write(y_offset, 0, row_no, self.format_title_data) 
            sheet.write(y_offset, 1, record[0], date_format)  
            sheet.merge_range(y_offset, 2,y_offset, 3, record[1], self.format_title_data) 
            sheet.merge_range(y_offset, 4,y_offset, 6, record[2], self.format_title_data)
            sheet.write(y_offset, 7, record[3], self.format_title_data)  
            sheet.merge_range(y_offset, 8,y_offset, 10, record[4], self.format_title_data)
            sheet.merge_range(y_offset, 11,y_offset, 13, record[5], self.format_title_data)
            sheet.write(y_offset, 14, record[6], self.format_title_data)

            standard_price = self.env['product.product'].search([('id','=',record[7])], limit=1).standard_price

            sheet.merge_range(y_offset, 15,y_offset, 17, standard_price, self.format_title_data)
            sheet.merge_range(y_offset, 18,y_offset, 20, record[6] * standard_price, self.format_title_data)                        
            y_offset += 1
                           
        workbook.close()
        output.seek(0)
        # response.stream.write(output.read())
        generated_file = output.read()
        output.close()

        return generated_file
         
    def xlsx_export(self,datas):  
        #data = self.get_report_values(self._ids, datas)
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': 'report.inventory.adjustment',
                         'options': json.dumps(datas),
                         'output_format': 'xlsx',
                         'financial_id': self.env.context.get('id'),
                         }
                }
        
    
    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
         * format_header_right
         * format_header_italic
         * format_border_top
        """
        self.format_title_company = workbook.add_format({
            'bold': True,
            'align': 'center',
        })
        self.format_title_data = workbook.add_format({
            'border': True,
            'align': 'center',
        })
        self.format_question = workbook.add_format({
            'border': True,
            'align': 'center',
            'bg_color': '#FFFFCC',
        })
        self.format_answer = workbook.add_format({
            'border': True,
            'align': 'left',            
        })
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 14,
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True
        })
        self.format_header_right = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'align': 'right'
        })
        self.format_header_center = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'align': 'center'
        })
        self.format_header_italic = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'italic': True
        })
        self.format_border_top = workbook.add_format({
            'border': True,
            'align': 'center'
        })
        self.product_format = workbook.add_format({
            'border': True,
            'align': 'left'
        })
        self.format_header_one = workbook.add_format({
            'align': 'center',
            'bold': True,
            'border': True,
        })