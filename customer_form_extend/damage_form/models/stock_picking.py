from odoo import models, fields, api
from datetime import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    damaged_id = fields.Many2one(
        'damage.product', "Damage StockPicking Id",
        index=True, ondelete='cascade')
    damaged_remark = fields.Text(string="Damaged Remark")
    # issued_date = fields.Date(string='Received Date',default=fields.Date.today(),track_visibility='always')

    @property
    def action_done(self):
        res = super(StockPicking,self).action_done
        if self.sample_id:
            sample_obj = self.env['sample.give'].search([('id','=',self.sample_id.id)])
            for line in self.move_line_ids_without_package:
                for l in sample_obj.product_line:
                    if line.product_id == l.product_id:
                        if self.transfer_type == 'sample':
                            l.deliver_qty += line.qty_done
                            l.balance_qty = l.deliver_qty - l.return_qty
                        elif self.transfer_type == 'sample_return':
                            l.return_qty += line.qty_done
                            l.balance_qty = l.deliver_qty - l.return_qty
        elif self.damaged_id:
            damage_obj = self.env['damage.product'].search([('id','=',self.damaged_id.id)])
            for line in self.move_line_ids_without_package:
                for l in damage_obj.product_line:
                    if line.product_id == l.product_id:
                        if self.transfer_type == 'damage_delivery':
                            l.deliver_qty += line.qty_done
                            l.balance_qty = l.deliver_qty - l.return_qty
                        elif self.transfer_type == 'damage_return':
                            l.return_qty += line.qty_done
                            l.balance_qty = l.deliver_qty - l.return_qty
        return res
