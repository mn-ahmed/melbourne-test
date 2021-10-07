 # -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api


class PurchaseItemListReportWizard(models.TransientModel):
    _name = 'purchase.item.list.wizard'
    _description = 'Purchase Item List Report'

    start_date = fields.Date(
        string="Start Date",
        required=True
    )
    end_date = fields.Date(
        string="End Date",
        required=True
    )

    def view_purchase_item_list_report(self):

        domain = []

        domain.append(('date_order','>=',self.start_date))
        domain.append(('date_order','<=',self.end_date))

        all_item_list_reports = self.env['purchase.item.list'].search(domain)

        return {
            'type': 'ir.actions.act_window',
            'name': ('Purchase Item List Report'),
            'res_model': 'purchase.item.list',
            'view_mode': 'tree,pivot',
            'domain' : [('id','in', all_item_list_reports.ids)],
        }
        