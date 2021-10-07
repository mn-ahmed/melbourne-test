from odoo import api, models, fields, tools, _


class NetSaleReport(models.Model):

    _name = 'net.sale.report'
    _description = "Net Sale Report"
    _auto = False
    _rec_name = 'inv_number'
    _order = 'inv_number desc'

    date = fields.Date('Date')
    inv_number = fields.Char('Voucher No.')
    partner_id = fields.Many2one('res.partner', 'Consignee/Buyer')
    sale_man_id = fields.Many2one('res.users', 'Sale Man Name')
    sale_team_id = fields.Many2one('crm.team', 'Sale Team')
    item_code = fields.Char('Item Code')
    brand_id = fields.Many2one('product.brand', 'Category')
    sale_qty = fields.Float('Sale Qty')
    sale_amt = fields.Float('Sale Amount')
    returned_qty = fields.Float('Return Qty')
    returned_amt = fields.Float('Returned Amount')
    net_sale_qty = fields.Float('Net Sale Qty')
    net_sale_amt = fields.Float('Net Sale Amount')
    product_cost = fields.Float('Purchase Rate')
    branch_id = fields.Many2one('res.branch', 'Branch')
    delivery_address = fields.Char('Party Address')
    contact_person = fields.Char('Party Contact Person')
    contact_telephone = fields.Char('Party Telephone No.')
    contact_mobile = fields.Char('Party Mobile No.')

    @staticmethod
    def _query(with_clause='', fields={}, group_by='', from_clause='', where=''):

        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
                        ID,
                        DATE,
                        INV_NUMBER,
                        PARTNER_ID,
                        SALE_MAN_ID,
                        SALE_TEAM_ID,
                        ITEM_CODE,
                        BRAND_ID,
                        SALE_QTY,
                        SALE_AMT,
                        RETURNED_QTY,
                        RETURNED_AMT,
                        (COALESCE(SALE_QTY, 0) + COALESCE(RETURNED_QTY, 0)) AS NET_SALE_QTY,
                        (COALESCE(SALE_AMT, 0) + COALESCE(RETURNED_AMT, 0)) AS NET_SALE_AMT,
                        PRODUCT_COST,
                        BRANCH_ID,
                        DELIVERY_ADDRESS,
                        CONTACT_PERSON,
                        CONTACT_TELEPHONE,
                        CONTACT_MOBILE
        """

        for field in fields.values():
            select_ += field

        from_ = """
                (
                SELECT		MOVE_LINE.ID AS ID,
                            MOVE.INVOICE_DATE AS DATE,
                            MOVE.NAME AS INV_NUMBER,
                            MOVE.PARTNER_ID AS PARTNER_ID,
                            MOVE.INVOICE_USER_ID AS SALE_MAN_ID,
                            MOVE.TEAM_ID AS SALE_TEAM_ID,
                            PT.DEFAULT_CODE AS ITEM_CODE,
                            PT.BRAND_ID AS BRAND_ID,
                            MOVE_LINE.QUANTITY AS SALE_QTY,
                            MOVE_LINE.PRICE_SUBTOTAL AS SALE_AMT,
                            (
                                SELECT 	SUM(-AML.QUANTITY)
                                FROM	ACCOUNT_MOVE_LINE AML
                                        LEFT JOIN ACCOUNT_MOVE AM ON AM.ID=AML.MOVE_ID
                                        LEFT JOIN SALE_ORDER_LINE_INVOICE_REL SO_AC_REL ON SO_AC_REL.INVOICE_LINE_ID=AML.ID
                                        LEFT JOIN SALE_ORDER_LINE SO_LINE ON SO_LINE.ID=SO_AC_REL.ORDER_LINE_ID
                                WHERE	AM.TYPE='out_refund' AND AM.STATE='posted' AND SO_LINE.ID=ORDER_LINE.ID
                            ) AS RETURNED_QTY,
                            (
                                SELECT 	SUM(-AML.PRICE_SUBTOTAL)
                                FROM	ACCOUNT_MOVE_LINE AML
                                        LEFT JOIN ACCOUNT_MOVE AM ON AM.ID=AML.MOVE_ID
                                        LEFT JOIN SALE_ORDER_LINE_INVOICE_REL SO_AC_REL ON SO_AC_REL.INVOICE_LINE_ID=AML.ID
                                        LEFT JOIN SALE_ORDER_LINE SO_LINE ON SO_LINE.ID=SO_AC_REL.ORDER_LINE_ID
                                WHERE	AM.TYPE='out_refund' AND AM.STATE='posted' AND SO_LINE.ID=ORDER_LINE.ID
                            ) AS RETURNED_AMT,
                            (
                                SELECT VALUE_FLOAT  FROM IR_PROPERTY 
                                WHERE NAME='standard_price' AND RES_ID='product.product,' || PP.ID 
                            ) AS PRODUCT_COST,
                            MOVE.BRANCH_ID AS BRANCH_ID,
                            CASE
                                WHEN PARTNER.TOWNSHIP_ID IS NULL THEN
                                    CASE 
                                        WHEN PARTNER.STREET IS NOT NULL AND PARTNER.STREET2 IS NOT NULL 
                                        THEN PARTNER.STREET || ', ' || PARTNER.STREET2
                                        WHEN PARTNER.STREET IS NOT NULL AND PARTNER.STREET2 IS NULL
                                        THEN PARTNER.STREET
                                        WHEN PARTNER.STREET IS NULL AND PARTNER.STREET2 IS NOT NULL
                                        THEN PARTNER.STREET2
                                        ELSE NULL
                                    END
                                ELSE
                                    CASE 
                                        WHEN PARTNER.STREET IS NOT NULL AND PARTNER.STREET2 IS NOT NULL 
                                        THEN PARTNER.STREET || ', ' || PARTNER.STREET2 || ', ' || TOWNSHIP.NAME
                                        WHEN PARTNER.STREET IS NOT NULL AND PARTNER.STREET2 IS NULL
                                        THEN PARTNER.STREET || ', ' || TOWNSHIP.NAME
                                        WHEN PARTNER.STREET IS NULL AND PARTNER.STREET2 IS NOT NULL
                                        THEN PARTNER.STREET2 || ', ' || TOWNSHIP.NAME
                                        ELSE NULL
                                    END
                            END AS DELIVERY_ADDRESS,
                            (
                                SELECT NAME FROM RES_PARTNER WHERE PARENT_ID=MOVE.PARTNER_ID AND TYPE='contact' LIMIT 1
                            ) AS CONTACT_PERSON,
                            PARTNER.PHONE AS CONTACT_TELEPHONE,
                            PARTNER.MOBILE AS CONTACT_MOBILE
                    
                    FROM    ACCOUNT_MOVE_LINE MOVE_LINE
                            LEFT JOIN ACCOUNT_MOVE MOVE ON MOVE.ID=MOVE_LINE.MOVE_ID
                            LEFT JOIN RES_PARTNER PARTNER ON PARTNER.ID=MOVE.PARTNER_ID
                            LEFT JOIN RES_TOWNSHIP TOWNSHIP ON TOWNSHIP.ID=PARTNER.TOWNSHIP_ID
                            LEFT JOIN SALE_ORDER_LINE_INVOICE_REL REL ON REL.INVOICE_LINE_ID=MOVE_LINE.ID
                            LEFT JOIN SALE_ORDER_LINE ORDER_LINE ON ORDER_LINE.ID=REL.ORDER_LINE_ID
                            LEFT JOIN PRODUCT_PRODUCT PP ON PP.ID=MOVE_LINE.PRODUCT_ID
                            LEFT JOIN PRODUCT_TEMPLATE PT ON PT.ID=PP.PRODUCT_TMPL_ID
                            
                    WHERE   MOVE.TYPE='out_invoice' 
                            AND MOVE.STATE='posted' 
                            AND MOVE_LINE.EXCLUDE_FROM_INVOICE_TAB=FALSE
                ) AS NET_SALE_REPORT
                %s
            """ % from_clause

        return '%s (SELECT %s FROM %s)' % (with_, select_, from_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
