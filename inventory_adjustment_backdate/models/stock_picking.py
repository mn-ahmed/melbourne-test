from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        super(StockPicking, self).action_done()
        self.write({'date_done': self.scheduled_date})
        self.move_line_ids.write({'date': self.scheduled_date})
        self.move_lines.write({'date': self.scheduled_date})

