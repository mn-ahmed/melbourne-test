 # -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _


class CustomerCreditLimitReportWizard(models.TransientModel):
    _name = 'credit.limit.report.wizard'
    _description = 'Customer Credit Limit Report'

    start_date = fields.Date(
        string="Start Date",
        required=True
    )
    end_date = fields.Date(
        string="End Date",
        required=True
    )

    def view_customer_credit_limit_report(self):

        domain = []

        domain.append(('invoice_date','>=',self.start_date))
        domain.append(('invoice_date','<=',self.end_date))

        all_records = self.env['credit.limit.report'].search(domain)

        return {
            'type': 'ir.actions.act_window',
            'name': ('Customer Credit Limit Report'),
            'res_model': 'credit.limit.report',
            'view_mode': 'tree,pivot',
            'domain' : [('id','in', all_records.ids)],
            'context': {'group_by': 'partner_id'}
        }
        