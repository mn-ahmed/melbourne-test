# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)
import xlsxwriter
from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo import http
from odoo.http import content_disposition, request
import json
from odoo.exceptions import Warning
from odoo import models, fields, api, _
import itertools,operator
import logging
_logger = logging.getLogger(__name__)
from io import StringIO
import io
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class Incoming_Report(models.TransientModel):
    _name = 'inventory.adjust.report'
    _description = 'Inventory Adjust Report'

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse')
    location_id = fields.Many2one(comodel_name='stock.location', string='Location')
    start_date = fields.Date('Beginning Date', required=True)
    end_date = fields.Date('End Date', required=True)
    
    @api.onchange('warehouse_id')
    def onchange_warehouse(self):
        """
        Make warehouse compatible with company
        """
        location_obj = self.env['stock.location']
        location_ids = location_obj.search([('usage', '=', 'internal')])
        total_warehouses = self.warehouse_id
        if total_warehouses:
            addtional_ids = []
            for warehouse in total_warehouses:
                store_location_id = warehouse.view_location_id.id
                addtional_ids.extend([y.id for y in location_obj.search([('location_id', 'child_of', store_location_id), ('usage', '=', 'internal')])])
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
        
    
    def export_excel(self):
         
        data_obj = self.env['report.inventory.adjustment']
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        datas = {
                 'form':
                        {                            
                            'warehouse_id': self.warehouse_id.id,
                            'location_id': self.location_id.id,
                            'start_date': self.start_date.strftime(DF),
                            'end_date': self.end_date.strftime(DF),
                        }
                }
 
        return data_obj.xlsx_export(datas)