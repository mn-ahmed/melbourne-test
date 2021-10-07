import time
import json
import datetime
import io
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class POListWizard(models.TransientModel):
    _name = "polist.xlsx.report.wizard"
    _description = 'For po list by excel report'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    supplier_id = fields.Many2many("res.partner", required=True)

    def print_xlsx(self):
        suppliers = []
        if self.from_date > self.to_date:
            raise ValidationError('Start Date must be less than End Date')

        if self.supplier_id:

            # raise ValidationError('YOU NEED TO CHOOSE SUPPLIERS')
            for sup in self.supplier_id:
                suppliers.append(sup.id)

        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'supplier_id': suppliers,
        }
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {
                'model': 'polist.xlsx.report.wizard',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'PO List By Excel Report',
            }
        }

    def _purchse_order_within_date(self, from_date, to_date, supplier_id):
        if supplier_id:
            self._cr.execute(
                '''SELECT rp.id as rpid, rp.sequence_id as vendor, rp.name as vendor_name ,po.name as o_reference,
                    crp.name as contact,pt.name as Item,pol.name as Description,am.name as bill_name, pt.default_code as code,
                    pol.product_qty as qty,pu.name,pol.price_subtotal as amount,po.date_order as o_date,st.name as deli_name,
                    cur.symbol as currency,cur.id as currency_id,pol.qty_received,pol.qty_invoiced,aml.price_subtotal as bill_amount,
                    pol.price_unit,Max(po.date_approve::timestamp::date) as last_date 
                    FROM purchase_order po
                        LEFT JOIN res_partner rp ON(rp.id = po.partner_id)
                        LEFT JOIN res_partner crp ON(crp.parent_id = rp.id)
                        LEFT JOIN purchase_order_line pol ON(po.id = pol.order_id)
                        LEFT JOIN product_product pp ON(pp.id = pol.product_id)
                        LEFT JOIN product_template pt ON(pt.id = pp.product_tmpl_id)
                        LEFT JOIN uom_uom pu ON(pu.id = pol.product_uom)
                        LEFT JOIN account_move_line aml ON(aml.purchase_line_id = pol.id)
                        LEFT JOIN account_move am ON(am.id = aml.move_id)
                        LEFT JOIN res_currency cur ON(po.currency_id=cur.id)
                        -- LEFT JOIN res_currency_rate cr ON(cur.id=cr.currency_id)
                        LEFT JOIN stock_picking st ON(st.purchase_id = po.id)
                    WHERE po.date_approve >= %s
                    AND po.date_approve <= %s
                    AND rp.id in %s
                    GROUP BY rp.id, rp.name,crp.name,cur.symbol,cur.id,pt.name,pol.name,pol.product_qty,
                        po.date_order,pu.name,pol.price_subtotal,po.date_approve,po.name, pt.default_code,
                        pol.qty_received,pol.qty_invoiced,pol.price_unit,aml.price_subtotal,am.name,st.name
                    -- ORDER BY po.name               ''',
                (from_date, to_date, tuple(supplier_id)))
        values = self._cr.dictfetchall()
        return values

    def get_report_name(self):
        return _('PO List By Excel Report')

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        from_date = str(data['from_date'])
        to_date = str(data['to_date'])
        if len(data['supplier_id']) > 0:
            supplier_ids = data['supplier_id']

        elif len(data['supplier_id']) <= 0:
            raise ValidationError('PLEASE CHOOSE SUPPLIER FOR PRINT EXCEL ')

        order_ids = self._purchse_order_within_date(from_date, to_date,
                                                    supplier_ids)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('PO List Excel Report.xlsx')
        sheet.set_column(0, 21, 25)
        format1 = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'top': 1,
            'bottom': 1
        })
        format2 = workbook.add_format({
            'num_format': 'mm/dd/yy',
            'font_size': 12
        })
        format3 = workbook.add_format({'font_size': 12})
        format6 = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'top': 1,
            'bottom': 1
        })
        format7 = workbook.add_format({
            'bottom': 2,
        })
        format9 = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'top': 1,
            'bottom': 1
        })
        format9.set_align('right')
        head = workbook.add_format({'font_size': 14, 'bold': True})
        header = self.get_report_name(
        ) + '  From Date ' + from_date + ' To Date ' + to_date
        y_offset = 1
        sheet.merge_range(y_offset, 0, y_offset, 4, _(header), head)
        y_offset += 2
        sheet.write(y_offset, 0, _('Vendor ID'), format1)
        sheet.write(y_offset, 1, _('Name'), format1)
        sheet.write(y_offset, 2, _('Contact'), format1)
        sheet.write(y_offset, 3, _('Order Date'), format1)
        sheet.write(y_offset, 4, _('Order Reference'), format1)
        sheet.write(y_offset, 5, _('Deliver No'), format1)
        sheet.write(y_offset, 6, _('Vendor Bill No'), format1)
        sheet.write(y_offset, 7, _('Item Code'), format1)
        sheet.write(y_offset, 8, _('Item'), format1)
        sheet.write(y_offset, 9, _('Order Qty'), format9)
        sheet.write(y_offset, 10, _('Received Qty'), format9)
        sheet.write(y_offset, 11, _('Biled Qty'), format9)
        sheet.write(y_offset, 12, _('Unit of Measure'), format1)
        sheet.write(y_offset, 13, _('Unit Price'), format9)
        sheet.write(y_offset, 14, _('PO Amount(USD)'), format9)
        sheet.write(y_offset, 15, _('PO Amount(CNY)'), format9)
        sheet.write(y_offset, 16, _('PO Amount(MMK)'), format9)
        sheet.write(y_offset, 17, _('Billed Amount(USD)'), format9)
        sheet.write(y_offset, 18, _('Billed Amount(CNY)'), format9)
        sheet.write(y_offset, 19, _('Billed Amount(MMK)'), format9)
        sheet.write(y_offset, 20, _('Last Purchase Date'), format1)
        y_offset += 1
        if order_ids:
            vendor_id = None
            subtotal = 0
            subtotal_usd = 0
            subtotal_yuan = 0
            quantity = 0
            qty_received = 0
            total_qty = 0
            qty_invoiced = 0
            bill_amount = 0
            bill_amount_usd = 0
            bill_amount_yuan = 0
            total_qty_received = 0
            total_qty_invoiced = 0
            total_bill_amount_usd = 0
            total_bill_amount_yuan = 0
            total_bill_amount = 0
            total = 0
            usd_total = 0
            yuan_total = 0
            for line in order_ids:
                rate = 1
                if line['currency'] == 'K':
                    num_f = '#,##0.00' + line['currency']
                else:
                    num_f = line['currency'] + '#,##0.00'

                def_num_f = '#,##0.00;'

                query = """SELECT rate FROM res_currency_rate WHERE currency_id=""" + (
                    str(line['currency_id'])) + """ AND name <= '""" + str(
                    line['o_date']) + """' ORDER BY create_date DESC LIMIT 1""";
                self.env.cr.execute(query)
                result = self.env.cr.dictfetchall()
                for res in result:
                    rate = res['rate']
                format4 = workbook.add_format({
                    'font_size': 12,
                    'bold': True,
                    'top': 1,
                    'bottom': 1,
                    'num_format': num_f
                })
                format4_qty = workbook.add_format({
                    'font_size': 12,
                    'bold': True,
                    'top': 1,
                    'bottom': 1,
                })
                format5 = workbook.add_format({
                    'font_size': 12,
                    'bold': True,
                    'top': 1,
                    'bottom': 1,
                    'num_format': def_num_f
                })
                format8 = workbook.add_format({
                    'font_size': 12,
                })
                format_currency = workbook.add_format({
                    'font_size': 12,
                    'num_format': num_f,
                })
                num_k = '#,##0.00 K'
                c_kyat = workbook.add_format({
                    'font_size': 12,
                    'num_format': num_k
                })
                format4.set_align('right')
                format4_qty.set_align('right')
                format5.set_align('right')
                format8.set_align('right')
                format_currency.set_align('right')
                c_kyat.set_align('right')
                if not vendor_id:
                    vendor_id = line['rpid']
                if vendor_id == line['rpid']:
                    quantity += line['qty']
                    qty_received += line['qty_received']
                    qty_invoiced += line['qty_invoiced']
                    # subtotal += line['amount']
                    if line['currency'] == '$':
                        subtotal_usd += (line['amount'])
                        subtotal += (line['amount']) / rate
                    elif line['currency'] == '¥':
                        subtotal_yuan += (line['amount'])
                        subtotal += (line['amount']) * rate
                    else:
                        subtotal += line['amount']
                    if line['bill_amount']:
                        if line['currency'] == '$':
                            bill_amount_usd += line['bill_amount']
                            bill_amount += (line['bill_amount'] / rate)
                        elif line['currency'] == '¥':
                            bill_amount_yuan += line['bill_amount']
                            bill_amount += (line['bill_amount'] / rate)
                        else:
                            bill_amount += line['bill_amount']
                    else:
                        bill_amount += 0
                else:
                    y_offset += 1
                    col = 0
                    while col < 21:
                        sheet.write(y_offset, col, '', format4)
                        col += 1
                    sheet.write(y_offset, 9, quantity, format4_qty)
                    sheet.write(y_offset, 10, qty_received, format4_qty)
                    sheet.write(y_offset, 11, qty_invoiced, format4_qty)
                    sheet.write(y_offset, 14, _(subtotal_usd), format4)
                    sheet.write(y_offset, 15, _(subtotal_yuan), format4)
                    sheet.write(y_offset, 16, _(subtotal), format4)
                    sheet.write(y_offset, 17, _(bill_amount_usd), format4)
                    sheet.write(y_offset, 18, _(bill_amount_yuan), format4)
                    sheet.write(y_offset, 19, _(bill_amount), format4)
                    y_offset += 2
                    quantity = 0
                    qty_received = 0
                    qty_invoiced = 0
                    subtotal = 0
                    subtotal_usd = 0
                    subtotal_yuan = 0
                    bill_amount_usd = 0
                    bill_amount_yuan = 0
                    bill_amount = 0
                    vendor_id = line['rpid']
                    quantity += line['qty']
                    qty_received += line['qty_received']
                    qty_invoiced += line['qty_invoiced']
                    if line['currency'] == '$':
                        subtotal_usd += (line['amount'])
                        subtotal += (line['amount'] / rate)
                    elif line['currency'] == '¥':
                        subtotal_yuan += (line['amount'])
                        subtotal += (line['amount'] / rate)
                    else:
                        subtotal += line['amount']
                    if line['bill_amount']:
                        if line['currency'] == '$':
                            bill_amount_usd += (line['bill_amount'])
                            bill_amount += (line['bill_amount'] / rate)
                        elif line['currency'] == '¥':
                            bill_amount_yuan += (line['bill_amount'])
                            bill_amount += (line['bill_amount'] / rate)
                        else:
                            bill_amount += line['bill_amount']
                    else:
                        bill_amount += 0
                sheet.write(y_offset, 0, line['vendor'], format3)
                sheet.write(y_offset, 1, line['vendor_name'], format3)
                sheet.write(y_offset, 2, line['contact'], format3)
                o_date = line['o_date'].strftime("%m/%d/%y")
                sheet.write(y_offset, 3, o_date, format3)
                sheet.write(y_offset, 4, line['o_reference'], format3)
                sheet.write(y_offset, 5, line['deli_name'], format3)
                sheet.write(y_offset, 6, line['bill_name'], format3)
                sheet.write(y_offset, 7, line['code'], format3)
                sheet.write(y_offset, 8, line['item'], format3)
                sheet.write(y_offset, 9, line['qty'], format8)
                sheet.write(y_offset, 10, line['qty_received'], format8)
                sheet.write(y_offset, 11, line['qty_invoiced'], format8)
                sheet.write(y_offset, 12, line['name'], format3)
                sheet.write(y_offset, 13, line['price_unit'], format_currency)

                total_amt = 0.0
                bill_amt = 0.0

                if line['currency'] == '$':
                    sheet.write(y_offset, 14, line['amount'], format_currency)
                    total_amt = line['amount'] / rate
                    sheet.write(y_offset, 16, _(total_amt) or 0.0, c_kyat)
                    if line['bill_amount']:
                        bill_amt = line['bill_amount'] / rate
                    sheet.write(y_offset, 17, _(line['bill_amount']) or 0, format_currency)
                    sheet.write(y_offset, 19, _(bill_amt) or 0, c_kyat)
                elif line['currency'] == '¥':
                    sheet.write(y_offset, 15, line['amount'], format_currency)
                    total_amt = line['amount'] / rate
                    sheet.write(y_offset, 16, _(total_amt) or 0, c_kyat)
                    if line['bill_amount']:
                        bill_amt = line['bill_amount'] / rate
                    sheet.write(y_offset, 18, line['bill_amount'] or 0, format_currency)
                    sheet.write(y_offset, 19, _(bill_amt) or 0, c_kyat)
                else:
                    sheet.write(y_offset, 16, line['amount'], c_kyat)
                    sheet.write(y_offset, 19, line['bill_amount'] or 0, c_kyat)

                # sheet.write(y_offset, 19, line['bill_amount'], format_currency)
                date = line['last_date'].strftime("%m/%d/%y")
                sheet.write(y_offset, 20, date, format2)
                total_qty += line['qty']
                total_qty_received += line['qty_received']
                total_qty_invoiced += line['qty_invoiced']
                if line['currency'] == '$':
                    usd_total += (line['amount'])
                    total += (line['amount'] / rate)
                elif line['currency'] == '¥':
                    yuan_total += (line['amount'])
                    total += (line['amount'] / rate)
                else:
                    total += line['amount']
                if line['bill_amount']:
                    if line['currency'] == '$':
                        total_bill_amount_usd += line['bill_amount']
                        total_bill_amount += line['bill_amount'] / rate
                    elif line['currency'] == '¥':
                        total_bill_amount_yuan += line['bill_amount']
                        total_bill_amount += line['bill_amount'] / rate
                    else:
                        total_bill_amount += (line['bill_amount'])
                else:
                    total_bill_amount += 0
                y_offset += 1
            y_offset += 1
            col = 0
            while col < 21:
                sheet.write(y_offset, col, '', format4)
                col += 1
            sheet.write(y_offset, 9, quantity, format4_qty)
            sheet.write(y_offset, 10, qty_received, format4_qty)
            sheet.write(y_offset, 11, qty_invoiced, format4_qty)
            sheet.write(y_offset, 14, _(subtotal_usd), format4)
            sheet.write(y_offset, 15, _(subtotal_yuan), format4)
            sheet.write(y_offset, 16, _(subtotal), format4)
            sheet.write(y_offset, 17, _(bill_amount_usd), format4)
            sheet.write(y_offset, 18, _(bill_amount_yuan), format4)
            sheet.write(y_offset, 19, _(bill_amount), format4)
            y_offset += 2
            col = 0
            while col < 21:
                sheet.write(y_offset, col, '', format4)
                col += 1
            sheet.write(y_offset, 0, 'Report Totals', format6)
            sheet.write(y_offset, 9, total_qty, format4_qty)
            sheet.write(y_offset, 10, total_qty_received, format4_qty)
            sheet.write(y_offset, 11, total_qty_invoiced, format4_qty)
            sheet.write(y_offset, 14, _(usd_total), format5)
            sheet.write(y_offset, 15, _(yuan_total), format5)
            sheet.write(y_offset, 16, _(total), format5)
            sheet.write(y_offset, 17, total_bill_amount_usd, format5)
            sheet.write(y_offset, 18, total_bill_amount_yuan, format5)
            sheet.write(y_offset, 19, total_bill_amount, format5)
            y_offset += 3
        range = "A" + str(y_offset) + ":U" + str(y_offset)
        sheet.conditional_format(range, {'type': 'blanks', 'format': format7})
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
