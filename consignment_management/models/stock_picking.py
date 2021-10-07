from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

OPENING_QUERY = """
SELECT	PRODUCT_ID, LOC_ID, SUM(QTY) AS QTY
FROM(
        SELECT		PP.ID AS PRODUCT_ID, 
                    LOC.ID AS LOC_ID,
                    SUM(-PRODUCT_UOM_QTY) AS QTY
        FROM		PRODUCT_PRODUCT PP
                    LEFT JOIN STOCK_MOVE SM ON SM.PRODUCT_ID=PP.ID
                    LEFT JOIN STOCK_LOCATION LOC ON SM.LOCATION_ID=LOC.ID
        WHERE		SM.STATE='done' AND SM.DATE < %s AND LOC.USAGE='internal' 
                    AND PRODUCT_ID = %s AND LOC.ID = %s
        GROUP BY	PP.ID, LOC.ID
        UNION ALL
        SELECT		PP.ID AS PRODUCT_ID, 
                    LOC.ID AS LOC_ID,
                    SUM(PRODUCT_UOM_QTY) AS QTY
        FROM		PRODUCT_PRODUCT PP
                    LEFT JOIN STOCK_MOVE SM ON SM.PRODUCT_ID=PP.ID
                    LEFT JOIN STOCK_LOCATION LOC ON SM.LOCATION_DEST_ID=LOC.ID
        WHERE		SM.STATE='done' AND SM.DATE < %s AND LOC.USAGE='internal' 
                    AND PRODUCT_ID = %s AND LOC.ID = %s
        GROUP BY	PP.ID, LOC.ID
) OPENING 
GROUP   BY PRODUCT_ID, LOC_ID
"""


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    consignment = fields.Boolean('Is Consignment Picking?')
    consignment_transfer_id = fields.Many2one('consignment.transfer', 'Consignment Transfer')
    consignment_return_id = fields.Many2one('consignment.return', 'Consignment Return')

    @api.constrains('consignment')
    def check_consignment_transfers(self):
        for rec in self:
            if rec.consignment and (rec.picking_type_code != 'internal'):
                raise ValidationError(_('Operation type of consignment Delivery/Return should be internal.'))

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self:
            if not (picking.consignment or picking.sale_id.consignment_sale):
                continue
            if picking.consignment_transfer_id:
                picking.update_consignment_transfer_line()

            if picking.consignment_return_id:
                picking.update_consignment_return_line()

            partner_loc_id = picking.partner_id.consignment_location_id.id
            picking_type = False

            if partner_loc_id == picking.location_id.id:
                if picking.location_dest_id.usage == 'internal':
                    picking_type = 'return'
                elif picking.location_dest_id.usage == 'customer':
                    picking_type = 'order'

            elif partner_loc_id == picking.location_dest_id.id:
                if picking.location_id.usage == 'internal':
                    picking_type = 'delivery'
                elif picking.location_id.usage == 'customer':
                    picking_type = 'order_return'
            else:
                raise UserError(_('Please check your consignment partner and location.'))

            if not picking_type:
                return res

            for line in picking.move_lines:

                domain = [('date', '=', line.date.date()),
                          ('product_id', '=', line.product_id.id),
                          ('partner_id', '=', picking.partner_id.id),
                          ('location_id', '=', partner_loc_id)]
                consignment_report = self.env['consignment.stock.report'].search(domain)

                if consignment_report:
                    quantities = self.calculate_quantities(line=line,
                                                           report=consignment_report,
                                                           picking_type=picking_type,
                                                           opening_qty=consignment_report.opening_qty)
                    consignment_report.write({
                        'transferred_qty': quantities['transferred_qty'],
                        'returned_qty': quantities['returned_qty'],
                        'ordered_qty': quantities['ordered_qty'],
                        'closing_qty': quantities['closing_qty'],
                    })

                else:
                    self.env.cr.execute(OPENING_QUERY, (picking.scheduled_date.date(),
                                                        line.product_id.id,
                                                        partner_loc_id,
                                                        picking.scheduled_date.date(),
                                                        line.product_id.id,
                                                        partner_loc_id))
                    opening_result = self.env.cr.dictfetchall()
                    opening_qty = 0
                    if opening_result:
                        opening_qty = opening_result[0]['qty'] or 0

                    quantities = self.calculate_quantities(line=line,
                                                           report=False,
                                                           picking_type=picking_type,
                                                           opening_qty=opening_qty)
                    self.env['consignment.stock.report'].create({
                        'date': line.date.date(),
                        'product_id': line.product_id.id,
                        'partner_id': picking.partner_id.id,
                        'location_id': partner_loc_id,
                        'opening_qty': opening_qty,
                        'transferred_qty': quantities['transferred_qty'],
                        'returned_qty': quantities['returned_qty'],
                        'ordered_qty': quantities['ordered_qty'],
                        'closing_qty': quantities['closing_qty'],
                    })
        return res

    def update_consignment_transfer_line(self):

        self.consignment_transfer_id.state = 'deliver'

        if self.location_dest_id.is_consignment_location:
            for line in self.move_lines:
                if line.quantity_done > line.consignment_transfer_line_id.quantity:
                    raise UserError(_("Quantity shouldn't be more than requested from consignment transfer."))
                transfer_line = line.consignment_transfer_line_id
                line.consignment_transfer_line_id.write({
                    'delivered_qty': line.quantity_done + transfer_line.delivered_qty,
                    'qty_left': line.quantity_done + transfer_line.qty_left,
                })
        else:
            for line in self.move_lines:
                transfer_line = line.consignment_transfer_line_id
                returned_qty = transfer_line.returned_qty
                qty_left = transfer_line.qty_left
                line.consignment_transfer_line_id.write({
                    'returned_qty': line.quantity_done + returned_qty,
                    'qty_left': qty_left - line.quantity_done,
                })

    def update_consignment_return_line(self):
        self.consignment_return_id.state = 'deliver'
        for line in self.move_lines:
            return_line = line.consignment_return_line_id
            return_line.write({'delivered_qty': line.quantity_done})
            transfer_line = return_line.transfer_line_id
            if transfer_line:
                prev_returned_qty = transfer_line.returned_qty
                qty_left = transfer_line.qty_left
                transfer_line.write({
                    'returned_qty': line.quantity_done + prev_returned_qty,
                    'qty_left': qty_left - line.quantity_done,
                })

    @staticmethod
    def calculate_quantities(line, report, picking_type, opening_qty):

        if report:
            transferred_qty = report.transferred_qty
            returned_qty = report.returned_qty
            ordered_qty = report.ordered_qty
        else:
            transferred_qty = returned_qty = ordered_qty = 0

        if picking_type == 'delivery':
            transferred_qty += line.product_uom_qty
        elif picking_type == 'return':
            returned_qty += line.product_uom_qty
        elif picking_type == 'order':
            ordered_qty += line.product_uom_qty
        else:
            ordered_qty -= line.product_uom_qty

        closing_qty = opening_qty + transferred_qty - returned_qty - ordered_qty

        return {
            'opening_qty': opening_qty,
            'transferred_qty': transferred_qty,
            'returned_qty': returned_qty,
            'ordered_qty': ordered_qty,
            'closing_qty': closing_qty,
        }
