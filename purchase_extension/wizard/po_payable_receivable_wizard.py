import time
import json
import datetime
import io
from odoo import fields, models, _
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class POListWizard(models.TransientModel):
    _name = "popaybale.receviable.xlsx.report.wizard"
    _description = 'Receviable report'

    due_filter_date = fields.Date(string="Date", required=True)
    supplier_id = fields.Many2many("res.partner")

    def print_popaybale_receviable_xlsx(self):
        suppliers = []
        if self.supplier_id:
            for sup in self.supplier_id:
                suppliers.append(sup.id)
        else:
            suppliers = []
        data = {
            'due_filter_date': self.due_filter_date,
            'supplier_id': suppliers
        }
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {
                'model': 'popaybale.receviable.xlsx.report.wizard',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Aged Payable Excel Report',
            }
        }

    def _purchse_order_within_date(self, due_filter_date, supplier_ids):
        if supplier_ids:
            self._cr.execute(
                '''SELECT rp.id as rpid, rp.sequence_id as vendor, rp.name as vendor_name, 
                crp.name as contact,am.invoice_date as billdate,
                am.invoice_date_due as due_date,po.name as po_number,
                apt.name as Terms, DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) as age_day,
                am.name as vbillno,am.amount_residual as amount_due,
                cur.symbol as currency
                FROM purchase_order po
                    LEFT JOIN res_partner rp ON(rp.id = po.partner_id)
                    LEFT JOIN res_partner crp ON(crp.parent_id = rp.id)
                    LEFT JOIN purchase_order_line pol ON(po.id = pol.order_id)
                    LEFT JOIN product_product pp ON(pp.id = pol.product_id)
                    LEFT JOIN product_template pt ON(pt.id = pp.product_tmpl_id)
                    LEFT JOIN uom_uom pu ON(pu.id = pol.product_uom)
                    LEFT JOIN account_move_line aml ON(aml.purchase_line_id = pol.id)
                    LEFT JOIN account_move am ON(am.id = aml.move_id)
                    LEFT JOIN account_payment_term apt ON(apt.id = am.invoice_payment_term_id)
                    LEFT JOIN res_currency cur ON(po.currency_id=cur.id)
                WHERE am.invoice_date <= %s
                AND po.invoice_status = 'invoiced'
                AND rp.id in %s
                GROUP BY rp.id, rp.sequence_id, rp.name,
                crp.name,am.invoice_date,am.invoice_date_due,po.name,
                apt.name,am.invoice_date_due,
                am.name ,am.amount_residual,
                cur.symbol''', (due_filter_date, tuple(supplier_ids)))
        values = self._cr.dictfetchall()
        return values

    def get_report_name(self):
        return _('Age Payable as at ')

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        filter_date = str(data['due_filter_date'])
        supplier_ids = None
        if len(data['supplier_id']) > 0:
            supplier_ids = data['supplier_id']
        order_ids = self._purchse_order_within_date(filter_date, supplier_ids)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('PO List Excel Report.xlsx')
        sheet.set_column(0, 2, 20)
        sheet.set_column(3, 4, 8)
        sheet.set_column(5, 6, 15)
        sheet.set_column(7, 7, 8)
        sheet.set_column(8, 8, 12)
        sheet.set_column(9, 16, 15)
        sheet.set_row(1, 25)
        head = workbook.add_format({'font_size': 10, 'bold': True})
        format1 = format2 = format3 = format4 = format5 = format6 = format7 = format8 = format9 = None
        format1 = workbook.add_format({
            'font_size': 9,
            'bold': True,
            'top': 1,
            'bottom': 1
        })
        format2 = workbook.add_format({
            'num_format': 'mm/dd/yy',
            'font_size': 9
        })
        format3 = workbook.add_format({'font_size': 9})
        format6 = workbook.add_format({
            'font_size': 9,
            'bold': True,
        })
        format9 = workbook.add_format({
            'font_size': 9,
            'bold': True,
            'top': 1,
            'bottom': 1
        })
        bold_mmk_format = workbook.add_format({
            'font_size': 9, 'bold': True,
            'num_format': '#,##0.00K',
            'align': 'right',
            'font_name': 'Arial',
            'bottom': 1
        })
        bold_usd_format = workbook.add_format({
            'font_size': 9, 'bold': True,
            'num_format': '$#,##0.00',
            'align': 'right',
            'font_name': 'Arial',
            'bottom': 1
        })
        bold_cny_format = workbook.add_format({
            'font_size': 9, 'bold': True,
            'num_format': '¥#,##0.00',
            'align': 'right',
            'font_name': 'Arial',
            'bottom': 1
        })
        head.set_font_name('Arial')
        format1.set_font_name('Arial')
        format2.set_font_name('Arial')
        format3.set_font_name('Arial')
        format6.set_font_name('Arial')
        format9.set_font_name('Arial')
        head.set_align('center')
        format2.set_align('left')
        format9.set_align('right')
        header = self.get_report_name() + filter_date + ' Date '
        y_offset = 1
        sheet.merge_range(y_offset, 0, y_offset, 2, _(header), head)
        y_offset += 2
        sheet.write(y_offset, 0, _('Vendor ID'), format1)
        sheet.write(y_offset, 1, _('Name'), format1)
        sheet.write(y_offset, 2, _('Contact'), format1)
        sheet.write(y_offset, 3, _('Date'), format1)
        sheet.write(y_offset, 4, _('Due Date'), format1)
        sheet.write(y_offset, 5, _('P.O.No'), format1)
        sheet.write(y_offset, 6, _('Terms'), format1)
        sheet.write(y_offset, 7, _('Age Days'), format9)
        sheet.write(y_offset, 8, _('Invoice/CM#'), format1)
        sheet.write(y_offset, 9, _('Not Due'), format9)
        sheet.write(y_offset, 10, _('0-10'), format9)
        sheet.write(y_offset, 11, _('11-20'), format9)
        sheet.write(y_offset, 12, _('21-30'), format9)
        sheet.write(y_offset, 13, _('Over 30 Days'), format9)
        sheet.write(y_offset, 14, _('Amount Due(USD)'), format9)
        sheet.write(y_offset, 15, _('Amount Due(CNY)'), format9)
        sheet.write(y_offset, 16, _('Amount Due'), format9)
        y_offset += 1
        if order_ids:
            vendor_id = None
            total = 0
            total_0_under = 0
            total_10 = 0
            total_20 = 0
            total_30 = 0
            total_30_over = 0
            alltotal_0_under = 0
            alltotal_10 = 0
            alltotal_20 = 0
            alltotal_30 = 0
            alltotal_30_over = 0
            alltotal = 0
            vendor_code = ''
            vendor_name = ''
            sp = ''
            all_total_mmk = all_total_usd = all_total_cny = 0
            total_mmk = total_usd = total_cny = 0

            for line in order_ids:

                if not line['age_day']:
                    continue

                if line['currency'] == 'K':
                    num_f = '#,##0.00' + line['currency']
                else:
                    num_f = line['currency'] + '#,##0.00'
                format4 = workbook.add_format({
                    'font_size': 9,
                    'num_format': num_f,
                    'top': 1
                })
                format5 = workbook.add_format({
                    'font_size': 9,
                    'num_format': num_f,
                    'bold': True,
                })
                format7 = workbook.add_format({
                    'font_size': 9,
                    'num_format': num_f,
                    'bottom': 1,
                    'bold': True,
                })
                format8 = workbook.add_format({
                    'font_size': 9,
                    'num_format': num_f,
                })

                format4.set_font_name('Arial')
                format5.set_font_name('Arial')
                format7.set_font_name('Arial')
                format8.set_font_name('Arial')
                format4.set_align('right')
                format5.set_align('right')
                format7.set_align('right')
                format8.set_align('right')

                amt_due_mmk = line['amount_due']

                if not vendor_id:
                    vendor_id = line['rpid']
                    vendor_code = line['vendor']
                    vendor_name = line['vendor_name']
                if vendor_id == line['rpid']:

                    company = self.env.user.company_id
                    USD = self.env['res.currency'].search([('name', '=', 'USD')])
                    CNY = self.env['res.currency'].search([('name', '=', 'CNY')])
                    MMK = self.env['res.currency'].search([('name', '=', 'MMK')])

                    amt_due_usd = amt_due_cny = '-'

                    print('\n{}{}\n'.format(line['currency'], line['amount_due']))

                    if line['currency'] == '$':
                        amt_due_usd = line['amount_due']
                        amt_due_mmk = USD._convert(
                            line['amount_due'], MMK, company, line['billdate']
                        )
                        total_usd += amt_due_usd
                        all_total_usd += amt_due_usd

                    elif line['currency'] == '¥':
                        amt_due_cny = line['amount_due']
                        amt_due_mmk = CNY._convert(
                            line['amount_due'], MMK, company, line['billdate']
                        )
                        total_cny += amt_due_cny
                        all_total_cny += amt_due_cny

                    # else:
                    #     amt_due_mmk = line['amount_due']

                    if line['age_day'] < 0:
                        total_0_under += line['amount_due']
                        total += line['amount_due']
                    elif line['age_day'] <= 10:
                        total_10 += line['amount_due']
                        total += line['amount_due']
                    elif line['age_day'] <= 20:
                        total_20 += line['amount_due']
                        total += line['amount_due']
                    elif line['age_day'] <= 30:
                        total_30 += line['amount_due']
                        total += line['amount_due']
                    else:
                        total_30_over += line['amount_due']
                        total += line['amount_due']

                else:
                    sheet.merge_range(y_offset, 9, y_offset, 16, sp, format4)
                    y_offset += 1
                    sheet.write(y_offset, 0, vendor_code, format6)
                    sheet.write(y_offset, 1, vendor_name, format6)
                    sheet.write(y_offset, 9, '-', format7)
                    sheet.write(y_offset, 10, '-', format7)
                    sheet.write(y_offset, 11, '-', format7)
                    sheet.write(y_offset, 12, '-', format7)
                    sheet.write(y_offset, 13, '-', format7)
                    sheet.write(y_offset, 14, total_usd, bold_usd_format)
                    sheet.write(y_offset, 15, total_cny, bold_cny_format)
                    sheet.write(y_offset, 16, total_mmk, bold_mmk_format)
                    total_usd = total_cny = total_mmk = 0
                    alltotal_0_under += total_0_under
                    alltotal_10 += total_10
                    alltotal_20 += total_20
                    alltotal_30 += total_30
                    alltotal_30_over += total_30_over
                    alltotal += total
                    y_offset += 2
                    total = 0
                    total_0_under = 0
                    total_10 = 0
                    total_20 = 0
                    total_30 = 0
                    total_30_over = 0
                    vendor_code = ''
                    vendor_name = ''
                    vendor_id = line['rpid']
                    vendor_code = line['vendor']
                    vendor_name = line['vendor_name']
                    if line['age_day'] < 0:
                        total_0_under += line['amount_due']
                        total += line['amount_due']
                    if line['age_day'] <= 10 and line['age_day'] >= 0:
                        total_10 += line['amount_due']
                        total += line['amount_due']
                    if line['age_day'] <= 20 and line['age_day'] >= 10:
                        total_20 += line['amount_due']
                        total += line['amount_due']
                    if line['age_day'] <= 30 and line['age_day']:
                        total_30 += line['amount_due']
                        total += line['amount_due']
                    if line['age_day'] > 30:
                        total_30_over += line['amount_due']
                        total += line['amount_due']

                total_mmk += amt_due_mmk
                all_total_mmk += amt_due_mmk

                sheet.write(y_offset, 0, line['vendor'], format3)
                sheet.write(y_offset, 1, line['vendor_name'], format3)
                sheet.write(y_offset, 2, line['contact'], format3)
                sheet.write(y_offset, 3, line['billdate'], format2)
                sheet.write(y_offset, 4, line['due_date'], format2)
                sheet.write(y_offset, 5, line['po_number'], format3)
                sheet.write(y_offset, 6, line['terms'], format3)
                sheet.write(y_offset, 7, line['age_day'], format3)
                sheet.write(y_offset, 8, line['vbillno'], format3)

                if line['age_day'] < 0:
                    sheet.write(y_offset, 9, line['amount_due'], format8)
                else:
                    sheet.write(y_offset, 9, '-', format8)

                if line['age_day'] <= 10 and line['age_day'] >= 0:
                    sheet.write(y_offset, 10, line['amount_due'], format8)
                else:
                    sheet.write(y_offset, 10, '-', format8)

                if line['age_day'] <= 20 and line['age_day'] > 10:
                    sheet.write(y_offset, 11, line['amount_due'], format8)
                else:
                    sheet.write(y_offset, 11, '-', format8)

                if line['age_day'] <= 30 and line['age_day'] > 20:
                    sheet.write(y_offset, 12, line['amount_due'], format8)
                else:
                    sheet.write(y_offset, 12, '-', format8)

                if line['age_day'] > 30:
                    sheet.write(y_offset, 13, line['amount_due'], format8)
                else:
                    sheet.write(y_offset, 13, '-', format8)

                mmk_format = workbook.add_format({
                    'font_size': 9,
                    'num_format': '#,##0.00K',
                    'align': 'right',
                    'font_name': 'Arial'
                })
                usd_format = workbook.add_format({
                    'font_size': 9,
                    'num_format': '$#,##0.00',
                    'align': 'right',
                    'font_name': 'Arial'
                })
                cny_format = workbook.add_format({
                    'font_size': 9,
                    'num_format': '¥#,##0.00',
                    'align': 'right',
                    'font_name': 'Arial'
                })

                sheet.write(y_offset, 14, amt_due_usd, usd_format)
                sheet.write(y_offset, 15, amt_due_cny, cny_format)
                sheet.write(y_offset, 16, amt_due_mmk, mmk_format)

                y_offset += 1

            sheet.merge_range(y_offset, 9, y_offset, 16, sp, format4)

            y_offset += 1

            sheet.write(y_offset, 0, vendor_code, format6)
            sheet.write(y_offset, 1, vendor_name, format6)
            sheet.write(y_offset, 9, '-', format7)
            sheet.write(y_offset, 10, '-', format7)
            sheet.write(y_offset, 11, '-', format7)
            sheet.write(y_offset, 12, '-', format7)
            sheet.write(y_offset, 13, '-', format7)
            sheet.write(y_offset, 14, total_usd, bold_usd_format)
            sheet.write(y_offset, 15, total_cny, bold_cny_format)
            sheet.write(y_offset, 16, total_mmk, bold_mmk_format)

            y_offset += 2

            sheet.write(y_offset, 0, 'Report Totals', format6)

            alltotal_0_under += total_0_under
            alltotal_10 += total_10
            alltotal_20 += total_20
            alltotal_30 += total_30
            alltotal_30_over += total_30_over
            alltotal += total

            if alltotal_0_under:
                sheet.write(y_offset, 9, alltotal_0_under, format5)
            else:
                sheet.write(y_offset, 9, '-', format5)

            sheet.write(y_offset, 10, '-', format5)
            sheet.write(y_offset, 11, '-', format5)
            sheet.write(y_offset, 12, '-', format5)
            sheet.write(y_offset, 13, '-', format5)

            if all_total_usd > 0:
                sheet.write(y_offset, 14, all_total_usd, bold_usd_format)
            else:
                sheet.write(y_offset, 14, '-', bold_usd_format)

            if all_total_cny > 0:
                sheet.write(y_offset, 15, all_total_cny, bold_cny_format)
            else:
                sheet.write(y_offset, 15, '-', bold_cny_format)

            if all_total_mmk > 0:
                sheet.write(y_offset, 16, all_total_mmk, bold_mmk_format)
            else:
                sheet.write(y_offset, 16, '-', bold_mmk_format)

            y_offset += 2

        range = "A" + str(y_offset) + ":Q" + str(y_offset)
        sheet.conditional_format(range, {'type': 'blanks', 'format': format7})
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
