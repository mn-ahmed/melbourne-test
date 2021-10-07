from odoo import api, fields, models, _

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _anglo_saxon_sale_move_lines(
        self,
        name,
        product,
        uom,
        qty,
        price_unit,
        currency=False,
        amount_currency=False,
        fiscal_position=False,
        account_analytic=False,
        analytic_tags=False,
    ):
        res = super()._anglo_saxon_sale_move_lines(
            name,
            product,
            uom,
            qty,
            price_unit,
            currency=currency,
            amount_currency=amount_currency,
            fiscal_position=fiscal_position,
            account_analytic=account_analytic,
            analytic_tags=analytic_tags,
        )
        if res:
            res[0]["account_analytic_id"] = account_analytic and account_analytic.id
            res[0]["analytic_tag_ids"] = (
                analytic_tags
                and analytic_tags.ids
                and [(6, 0, analytic_tags.ids)]
                or False
            )
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    def _prepare_account_move_line(
            self, qty, cost, credit_account_id, debit_account_id, description
    ):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, description
        )
        # Add analytic account in debit line
        if not self.analytic_account_id or not res:
            return res

        for num in range(0, 2):
            if (
                    res[num][2]["account_id"]
                    != self.product_id.categ_id.property_stock_valuation_account_id.id
            ):
                res[num][2].update({"analytic_account_id": self.analytic_account_id.id})
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'type': 'entry',
                'branch_id': self.branch_id.id,
                'analytic_account_id': self.analytic_account_id.id,
            })
            new_account_move.post()

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super()._prepare_merge_moves_distinct_fields()
        fields.append("analytic_account_id")
        return fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analytic_account_id = fields.Many2one(related="move_id.analytic_account_id")

