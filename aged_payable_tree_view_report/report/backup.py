from odoo import tools
from odoo import api, fields, models

class AgedPayableReport(models.Model):
    _name = "aged.payable.report"
    _description = "Aged Payable Tree View Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'
    
    vendor_code = fields.Char("Vendor ID")
    vendor_name = fields.Char("Name")
    contact_name = fields.Char("Contact")
    branch = fields.Char("Branch")
    date = fields.Date("Date")
    due_date = fields.Date("Due Date")
    po_number = fields.Char("P.O.No")
    invoice_payment_term_id = fields.Char("Terms")
    age_day = fields.Integer("Age Days")
    vendor_bill = fields.Char("Invoice/CM#")
    total_0_under = fields.Char("Not Due")
    total_10 = fields.Char("1-10")
    total_20 = fields.Char("11-20")
    total_30 = fields.Char("21-30")
    total_30_over = fields.Char("Over 30 days")
    amount_due_usd = fields.Char("Amount Due(USD)")
    amount_due_cny = fields.Char("Amount Due(CNY)")
    amount_due_euro = fields.Char("Amount Due(Euro)")
    amount_due_mmk = fields.Char("Amount Due")    

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            am.id as id, 
            case when rp.vendor_code is not null
                then rp.vendor_code
                else rp.sequence_id
                end as vendor_code,
            rp.name as vendor_name, 
            crp.name as contact_name,
            branch.name as branch,
            am.invoice_date as date,
            am.invoice_date_due as due_date,
            am.invoice_origin as po_number,
            apt.name as invoice_payment_term_id, 
            DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) as age_day,
            am.name as vendor_bill,
            case when (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp)) <= 0
                then concat(round(-(aml.balance) / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                )
                else ''
                end as total_0_under,
            case when (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) >= 1) and (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) <= 10)
                then concat(round(-(aml.balance) / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                )
                else ''
                end as total_10,
            case when (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) > 10) and (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) <= 20)
                then concat(round(-(aml.balance) / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                )
                else ''
                end as total_20,
            case when (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) > 20) and (DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) <= 30)
                then concat(round(-(aml.balance) / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                )
                else ''
                end as total_30,
            case when DATE_PART('day', CURRENT_TIMESTAMP::timestamp - am.invoice_date_due::timestamp) > 30
                then concat(round(-(aml.balance) / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                )
                else ''
                end as total_30_over,
            case when cur.name ='USD'
                then concat('$',-(aml.balance))
                else '$0.0'
                end as amount_due_usd,
            case when cur.name ='CNY'
                then concat('¥',-(aml.balance))
                else '¥0.0'
                end as amount_due_cny,
            case when cur.name = 'EUR'
                then concat('EUR',-(aml.balance))
                else 'EUR 0.0' 
                end as amount_due_euro,
            case when cur.name = 'MMK'
                then CONCAT( CAST(-(aml.balance) AS TEXT),'K')
                else concat(round(-(aml.balance) / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                )
                end as amount_due_mmk
        """
        for field in fields.values():
            select_ += field
        from_ = """
                account_move_line aml
                    LEFT JOIN account_journal aj on (aj.id=aml.journal_id)
                    LEFT JOIN account_move am on (am.id=aml.move_id)
                    LEFT JOIN res_partner rp ON (rp.id=aml.partner_id)
                    LEFT JOIN res_partner crp ON(crp.parent_id = rp.id)
                    LEFT JOIN account_payment_term apt ON(apt.id = am.invoice_payment_term_id)
                    LEFT JOIN res_currency cur ON(am.currency_id=cur.id)
                    LEFT JOIN res_branch branch ON(am.branch_id=branch.id)
                %s
        """ % from_clause

        where_ = """
            aml.account_internal_type = 'payable' and 
            aml.full_reconcile_id is NULL and
            aml.reconciled = false
            %s
        """ % where

        groupby_ = """
            am.id, aj.id,am.id,rp.id,crp.id,apt.id,cur.id,branch.id,
            rp.vendor_code, 
            rp.sequence_id,
            rp.name, 
            crp.name,
            branch.name,
            am.invoice_date,
            am.invoice_date_due,
            am.invoice_origin,
            apt.name, 
            am.name,
            -(aml.balance),
            cur.name
            %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s WHERE %s GROUP BY %s)' % (with_, select_, from_, where_, groupby_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))