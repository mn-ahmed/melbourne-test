import pytz
from datetime import datetime

from odoo import api, fields, models

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        if move_lines:
            date = self._context.get('force_period_date', False)
            print('Acc Date', date)
            if not date and self.picking_id:
                picking_date = self.picking_id.scheduled_date

                local_tz_st = pytz.timezone(self.env.user.tz or 'UTC')
                if picking_date:
                    
                    scheduled_date_only = picking_date
                    start_d = scheduled_date_only.replace(tzinfo=pytz.utc).astimezone(local_tz_st)
                    start_date = datetime.strftime(start_d, DEFAULT_SERVER_DATETIME_FORMAT)
                    scheduled_date_only = datetime.strptime(
                        start_date, '%Y-%m-%d %H:%M:%S'
                    )
                    date = scheduled_date_only.date()

                    print('Date', date)
            if not date and self.date:
                picking_date = self.date

                local_tz_st = pytz.timezone(self.env.user.tz or 'UTC')
                if picking_date:
                    
                    scheduled_date_only = picking_date
                    start_d = scheduled_date_only.replace(tzinfo=pytz.utc).astimezone(local_tz_st)
                    start_date = datetime.strftime(start_d, DEFAULT_SERVER_DATETIME_FORMAT)
                    scheduled_date_only = datetime.strptime(
                        start_date, '%Y-%m-%d %H:%M:%S'
                    )
                    date = scheduled_date_only.date()

            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'type': 'entry',
            })
            new_account_move.post()

    def write(self, vals): #24/09/2019
        if self._context.get('inventory_date', False):
            if vals.get('state', '') == 'done':
                vals.update({
                    'date': self._context['inventory_date']
                })
        return super(StockMove, self).write(vals)


class StockMoveLine(models.Model): #24/09/2019
    _inherit = "stock.move.line"

    def write(self, vals): #24/09/2019
        if self._context.get('inventory_date', False):
            if vals.get('date', False) and 'product_uom_qty' in vals:
                vals.update({
                    'date': self._context['inventory_date']
                })
        return super(StockMoveLine, self).write(vals)
