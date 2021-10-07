from odoo import tools
from odoo import api, fields, models
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES


class PurchaseItemListReport(models.Model):
    _name = "purchase.item.list"
    _description = "Purchase Item List Report"
    _auto = False
    _rec_name = 'date_order'
    _order = 'date_order desc'

    vendor_code = fields.Char("Vendor ID")
    vendor_name = fields.Char("Name")
    contact_name = fields.Char("Contact")
    date_order = fields.Datetime("Order Date")
    o_reference = fields.Char("Order Reference")
    delivery_no = fields.Char("Delivery No")
    vendor_bill = fields.Char("Vendor Bill No")
    bill_date = fields.Date(string='Vendor Bill Date')
    default_code = fields.Char("Item Code")
    product_name = fields.Char("Item")
    order_qty = fields.Float("Order Qty")
    received_qty = fields.Float("Received Qty")
    billed_qty = fields.Float("Billed Qty")
    uom = fields.Char("Unit of Measure")
    unit_price = fields.Float("Unit Price")
    po_amt_usd = fields.Float("PO Amount(USD)")
    po_amt_cny = fields.Float("PO Amount(CNY)")
    po_amt_mmk = fields.Float("PO Amount(MMK)")
    po_amt_euro = fields.Float("PO Amount(Euro)")
    p_amt_usd = fields.Char(" PO Amount(USD)")
    p_amt_cny = fields.Char(" PO Amount(CNY)")
    p_amt_mmk = fields.Char(" PO Amount(MMK)")
    p_amt_euro = fields.Char(" PO Amount(Euro)")
    billed_amt_usd = fields.Char("Bi Amount(USD)")
    billed_amt_cny = fields.Char("Bi Amount(CNY)")
    billed_amt_mmk = fields.Char("Bi Amount(MMK)")
    billed_amt_euro = fields.Char("Bi Amount(Euro)")

    branch_id = fields.Many2one('res.branch', "Branch")

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            pol.id as id,
            partner.sequence_id as vendor_code,
            partner.name as vendor_name,
            crp.name as contact_name,
            po.date_order as date_order,
            po.name as o_reference,
            po.branch_id as branch_id,
            sp.name as delivery_no,
            am.name as vendor_bill,
            am.invoice_date as bill_date,
            pt.default_code as default_code,
            pt.name as product_name,
            pol.product_qty as order_qty,
            pol.qty_received as received_qty,
            pol.qty_invoiced as billed_qty,
            uom.name as uom,
            pol.price_unit as unit_price,
            
            case when cur.name ='USD'
                then concat(pol.price_subtotal ,'$')
                else concat('0.00','$')
                end as p_amt_usd,
            case when cur.name = 'CNY'
                then concat(pol.price_subtotal,'¥')
                else concat('0.00','¥')
                end as p_amt_cny,
            case when cur.name = 'MMK'
                then concat(pol.price_subtotal,'K')
                else concat(round(pol.price_subtotal / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                ) end as p_amt_mmk,
            case when cur.name = 'EUR'
                then concat(pol.price_subtotal,'€')
                else concat('0.00','€') end as p_amt_euro,
                
            
            case when cur.name ='USD'
                then pol.price_subtotal 
                else 0
                end as po_amt_usd,
            case when cur.name = 'CNY'
                then pol.price_subtotal 
                else 0
                end as po_amt_cny,
            case when cur.name = 'MMK'
                then pol.price_subtotal
                else (pol.price_subtotal / (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1)
                ) end as po_amt_mmk,
            case when cur.name = 'EUR'
                then pol.price_subtotal
                else 0 end as po_amt_euro,
                
            case when cur.name ='USD'
                then concat(aml.price_subtotal,'$')
                else concat('0.00','$')
                end as billed_amt_usd,
            case when cur.name ='CNY'
                then concat(aml.price_subtotal,'¥')
                else concat('0.00','¥')
                end as billed_amt_cny,
            case when cur.name = 'MMK'
                then concat(NULLIF(aml.price_subtotal,'0.00'),'K')
                else concat(round(NULLIF(aml.price_subtotal ,'0.00')/ (SELECT currency_rate.rate 
                                            FROM res_currency_rate currency_rate
                                            JOIN res_currency currency ON (currency_rate.currency_id = currency.id)
                                            WHERE currency.name = cur.name
                                            ORDER BY currency_rate.create_date DESC LIMIT 1),2),'K'
                ) end as billed_amt_mmk,
            case when cur.name ='EUR'
                then concat(aml.price_subtotal,'€')
                else concat('0.00','€') 
                end as billed_amt_euro
        """
        for field in fields.values():
            select_ += field
        from_ = """
                purchase_order_line pol
                join purchase_order po on (pol.order_id=po.id)  
                    left join res_partner partner on po.partner_id = partner.id
                    left join res_partner crp on(crp.parent_id = partner.id)   
                    left join product_product pp on (pol.product_id=pp.id)
                    left join product_template pt on (pp.product_tmpl_id=pt.id)
                    left join uom_uom uom on (uom.id = pol.product_uom)
                    left join account_move_line aml ON(aml.purchase_line_id = pol.id)
                    left join account_move am ON(am.id = aml.move_id)
                    left join res_currency cur ON(po.currency_id=cur.id)
                    left join res_currency_rate cr ON(cur.id=cr.currency_id)
                    left join stock_picking sp ON(sp.purchase_id = po.id)
                %s
        """ % from_clause

        where_ = """
            po.state !='cancel'
            %s
        """ % where

        groupby_ = """
            pol.id,
            partner.sequence_id,
            partner.name,
            crp.name,
            po.date_order,
            po.name,
            po.branch_id,
            
            sp.name,
            am.name,  
            am.invoice_date,          
            pt.default_code,
            pt.name,
            pol.product_qty,
            pol.qty_received,
            pol.qty_invoiced,
            uom.name,
            pol.price_unit,
            cur.name,
            pol.price_subtotal,
            aml.price_subtotal
            %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s WHERE %s GROUP BY %s)' % (with_, select_, from_, where_, groupby_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
