from odoo import api, models, fields, tools, _


class ConsignmentReport(models.Model):
    _name = 'consignment.report'
    _description = 'Consignment Report'
    _auto = False

    ref = fields.Char('Reference')
    date = fields.Date('Date')
    product_id = fields.Many2one('product.product', 'Product')
    partner_id = fields.Many2one('res.partner', 'Consignee')
    location_id = fields.Many2one('stock.location', 'Location')
    transferred_qty = fields.Float('Transferred Qty')
    returned_qty = fields.Float('Returned Qty')
    ordered_qty = fields.Float('Ordered Qty')
    qty_left = fields.Float('Qty to be Ordered')
    transfer_price = fields.Monetary('Transfer Price', currency_field='transfer_currency_id')
    sale_price = fields.Monetary('Sale Price', currency_field='sale_currency_id')
    transfer_currency_id = fields.Many2one('res.currency', 'Transfer Currency')
    sale_currency_id = fields.Many2one('res.currency', 'Sale Currency')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('deliver', 'Delivered'),
                              ('close', 'Closed'),
                              ('cancel', 'Cancelled')])
    ta_id = fields.Many2many('res.partner.category', related='partner_id.category_id')



    def _query(self):
        return f'''
        SELECT      ROW_NUMBER() OVER(ORDER BY DATE(TRANS.DATE)) AS ID,
                    TRANS.NAME AS REF,
                    DATE(TRANS.DATE) AS DATE,
                    LINE.PRODUCT_ID AS PRODUCT_ID,
                    TRANS.PARTNER_ID AS PARTNER_ID,
                    PARTNER.CONSIGNMENT_LOCATION_ID AS LOCATION_ID,
                    COALESCE(LINE.DELIVERED_QTY, 0) AS TRANSFERRED_QTY,
                    COALESCE(LINE.RETURNED_QTY, 0) AS RETURNED_QTY,
                    COALESCE(LINE.ORDERED_QTY, 0) AS ORDERED_QTY,
                    COALESCE(LINE.QTY_LEFT, 0) AS QTY_LEFT,
                    SOL.PRICE_UNIT AS SALE_PRICE,
                    LINE.PRICE_UNIT AS TRANSFER_PRICE,
                    CASE
                        WHEN SOL.CURRENCY_ID IS NOT NULL THEN SOL.CURRENCY_ID
                        ELSE (SELECT CURRENCY_ID FROM RES_COMPANY WHERE ID = {self.env.company.currency_id.id})
                    END AS SALE_CURRENCY_ID,
                    CASE
                        WHEN LINE.CURRENCY_ID IS NOT NULL THEN LINE.CURRENCY_ID
                        ELSE (SELECT CURRENCY_ID FROM RES_COMPANY WHERE ID = {self.env.company.currency_id.id})
                    END AS TRANSFER_CURRENCY_ID,
                    TRANS.STATE AS STATE
                  
        FROM        CONSIGNMENT_TRANSFER_LINE AS LINE
                    LEFT JOIN CONSIGNMENT_TRANSFER TRANS ON TRANS.ID=LINE.CONSIGNMENT_TRANSFER_ID
                    LEFT JOIN RES_PARTNER PARTNER ON PARTNER.ID=TRANS.PARTNER_ID
                    LEFT JOIN SALE_ORDER_LINE SOL ON SOL.TRANSFER_LINE_ID=LINE.ID

        WHERE       TRANS.STATE NOT IN ('cancel')

--                SELECT		ROW_NUMBER() OVER(ORDER BY DATE, PRODUCT_ID, LOCATION_ID) AS ID,
--                             DATE,
--                             PRODUCT_ID,
--                             PARTNER_ID,
--                             LOCATION_ID,
--                             COALESCE(TRANSFERRED_QTY, 0) AS TRANSFERRED_QTY,
--                             COALESCE(RETURNED_QTY, 0) AS RETURNED_QTY,
--                             COALESCE(ORDERED_QTY, 0) AS ORDERED_QTY,
--                             0 AS QTY_LEFT
--                 FROM
--                 (
--                 SELECT		SM.PRODUCT_ID,
--                             SM.PARTNER_ID,
--                             PARTNER.CONSIGNMENT_LOCATION_ID AS LOCATION_ID,
--                             DATE(SM.DATE),
--                             SM.SALE_LINE_ID,
--                             CASE
--                                 WHEN SL.USAGE='internal' AND SL.IS_CONSIGNMENT_LOCATION IS NOT TRUE
--                                      AND DL.USAGE='internal' AND DL.IS_CONSIGNMENT_LOCATION=TRUE
--                                 THEN SM.PRODUCT_UOM_QTY
--                                 ELSE 0
--                             END AS TRANSFERRED_QTY,
--                             CASE
--                                 WHEN SL.USAGE='internal' AND SL.IS_CONSIGNMENT_LOCATION=TRUE
--                                      AND DL.USAGE='internal' AND DL.IS_CONSIGNMENT_LOCATION IS NOT TRUE
--                                 THEN SM.PRODUCT_UOM_QTY
--                                 ELSE 0
--                             END AS RETURNED_QTY,
--                             CASE
--                                 WHEN SL.USAGE='internal' AND SL.IS_CONSIGNMENT_LOCATION=TRUE
--                                      AND DL.USAGE='customer'
--                                 THEN 
--                                     (SELECT COALESCE(SUM(PRODUCT_UOM_QTY), 0) 
--                                     FROM STOCK_MOVE SM_T 
--                                          LEFT JOIN STOCK_LOCATION SL_T ON SL_T.ID=SM_T.LOCATION_ID
--                                          LEFT JOIN STOCK_LOCATION DL_T ON DL_T.ID=SM_T.LOCATION_DEST_ID
--                                     WHERE SM_T.SALE_LINE_ID=SM.SALE_LINE_ID AND 
--                                           SL_T.USAGE='customer' AND 
--                                           DL_T.USAGE='internal' AND 
--                                           DL_T.IS_CONSIGNMENT_LOCATION=TRUE
--                                     GROUP BY SM_T.SALE_LINE_ID,PARTNER.TAG_ID_CUSTOM)
--                                 ELSE 0
--                             END AS ORDERED_QTY
                
--                 FROM		STOCK_MOVE SM
--                             LEFT JOIN STOCK_PICKING SP ON SP.ID=SM.PICKING_ID
--                             LEFT JOIN STOCK_LOCATION SL ON SL.ID=SM.LOCATION_ID
--                             LEFT JOIN STOCK_LOCATION DL ON DL.ID=SM.LOCATION_DEST_ID
--                             LEFT JOIN RES_PARTNER PARTNER ON PARTNER.ID=SM.PARTNER_ID
                
--                 WHERE		SM.STATE='done'
--                             AND (SL.USAGE='internal' AND SL.IS_CONSIGNMENT_LOCATION=TRUE OR 
--                                  DL.USAGE='internal' AND DL.IS_CONSIGNMENT_LOCATION=TRUE)
--                             AND NOT (SL.USAGE='customer' AND DL.USAGE='internal' AND DL.IS_CONSIGNMENT_LOCATION=TRUE)
--                 ) AS CONSIGNMENT_REPORT
        '''

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
