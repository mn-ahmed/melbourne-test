from odoo import fields, models, api, _


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.depends('location_id')
    def compute_warehouse(self):
        for record in self:
            if not record.location_id:
                continue
            warehouse = self.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', record.location_id.id)])
            if warehouse:
                record.warehouse_id = warehouse[0].id

    employee_id = fields.Many2one('hr.employee', 'Issue By')
    contact_person = fields.Char(string='Contact Person')
    contact_phone = fields.Char('Contact Phone')
    contact_address = fields.Char('Contact Address')
    accept_person = fields.Char(string='Accept Person')
    sale_remark = fields.Text("Sale Remark")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', compute=compute_warehouse, store=True, readonly=False)
    delivery_date = fields.Datetime(string='Delivery Date', index=True, copy=False)
