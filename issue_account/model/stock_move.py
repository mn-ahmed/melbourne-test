# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    sample_id = fields.Many2one('sample.give', 'Sample Issue', related="picking_id.sample_id")
    damaged_id = fields.Many2one('damage.product', "Damage Issue", related="picking_id.damaged_id")
    is_sample = fields.Boolean('Is Sample', related="sample_id.is_sample")
    is_damage = fields.Boolean('Is Damage', related="damaged_id.is_damage")

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        if self.is_sample:
            if self.picking_id.transfer_type == 'sample':
                debit_account_id = self.company_id.sample_account_id.id
                if not debit_account_id:
                    raise UserError(_('Please configure Damage Issue Account!'))
            elif self.picking_id.transfer_type == 'sample_return':
                credit_account_id = self.company_id.sample_account_id.id
                if not credit_account_id:
                    raise UserError(_('Please configure Damage Issue Account!'))

        if self.is_damage:
            if self.picking_id.transfer_type == 'damage_delivery':
                debit_account_id = self.company_id.damage_account_id.id
                if not debit_account_id:
                    raise UserError(_('Please configure Damage Issue Account!'))
            elif self.picking_id.transfer_type == 'damage_receipt':
                credit_account_id = self.company_id.damage_account_id.id
                if not credit_account_id:
                    raise UserError(_('Please configure Damage Issue Account!'))
        return super(StockMove, self)._prepare_account_move_line(qty=qty, cost=cost,
                                                                 credit_account_id=credit_account_id,
                                                                 debit_account_id=debit_account_id,
                                                                 description=description)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_sample = fields.Boolean('Sample Issue', related="move_id.is_sample")
    is_damage = fields.Boolean('Damage Issue', related="move_id.is_damage")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_sample_entry(self, sample_lines):
        line_dict = {}
        journal_id = False
        for line in sample_lines:
            product = line.product_id
            if product not in line_dict:

                accounts_data = product.product_tmpl_id.get_product_accounts()
                acc_valuation = accounts_data.get('stock_valuation', False)

                line_dict[product] = {
                    'account_id': acc_valuation.id,
                    'lines': line,
                }

                if not journal_id:
                    journal_id = accounts_data.get('stock_journal', False)
            else:
                line_dict[product]['lines'] += line

        if not journal_id:
            raise UserError(
                _('Please configure journal on product category!')
            )

        receivable_acc_id = self.company_id.sample_account_id.id

        if not receivable_acc_id:
            raise UserError(
                _('Please configure Sample Issue Account!')
            )

        lines = []
        for categ in line_dict:
            move_lines = line_dict[categ]['lines']
            account = line_dict[categ]['account_id']

            if not account:
                raise UserError(
                    _('Please configure Valuation account on product category!')
                )

            value = sum(
                l.qty_done * l.product_id.standard_price
                for l in move_lines
            )
            credit_line_vals = {
                'name': categ.display_name,
                'product_id': False,
                'quantity': 1,
                'product_uom_id': False,
                'ref': self.name,
                'partner_id': self.partner_id.id,
                'credit': value,
                'debit': 0,
                'account_id': account,
            }
            lines.append((0, 0, credit_line_vals))

        trans_value = sum(
            m.qty_done * m.product_id.standard_price for m in sample_lines
        )

        trans_debit_line_vals = {
            'name': self.name,
            'product_id': False,
            'quantity': 1,
            'product_uom_id': False,
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'credit': 0,
            'debit': trans_value,
            'account_id': receivable_acc_id,
        }

        lines.append((0, 0, trans_debit_line_vals))

        move_vals = {
            'journal_id': journal_id.id,
            'date': self.scheduled_date or fields.Date.today(),
            'ref': self.name,
            'line_ids': lines,
            'type': 'entry',
        }
        move = self.env['account.move'].sudo().create(move_vals)
        move.post()

    @api.model
    def _create_damage_entry(self, damage_lines):

        line_dict = {}
        journal_id = False
        for line in damage_lines:
            product = line.product_id
            if product not in line_dict:

                accounts_data = product.product_tmpl_id.get_product_accounts()
                acc_valuation = accounts_data.get('stock_valuation', False)

                line_dict[product] = {
                    'account_id': acc_valuation.id,
                    'lines': line,
                }

                if not journal_id:
                    journal_id = accounts_data.get('stock_journal', False)
            else:
                line_dict[product]['lines'] += line

        if not journal_id:
            raise UserError(
                _('Please configure journal on product category!')
            )

        receivable_acc_id = self.company_id.damage_account_id.id

        if not receivable_acc_id:
            raise UserError(
                _('Please configure Damage Issue Account!')
            )

        lines = []
        for categ in line_dict:
            move_lines = line_dict[categ]['lines']
            account = line_dict[categ]['account_id']

            if not account:
                raise UserError(
                    _('Please configure Valuation account on product category!')
                )

            value = sum(
                l.qty_done * l.product_id.standard_price
                for l in move_lines
            )
            credit_line_vals = {
                'name': categ.display_name,
                'product_id': False,
                'quantity': 1,
                'product_uom_id': False,
                'ref': self.name,
                'partner_id': self.partner_id.id,
                'credit': value,
                'debit': 0,
                'account_id': account,
            }
            lines.append((0, 0, credit_line_vals))

        trans_value = sum(
            m.qty_done * m.product_id.standard_price for m in damage_lines
        )

        trans_debit_line_vals = {
            'name': self.name,
            'product_id': False,
            'quantity': 1,
            'product_uom_id': False,
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'credit': 0,
            'debit': trans_value,
            'account_id': receivable_acc_id,
        }

        lines.append((0, 0, trans_debit_line_vals))

        move_vals = {
            'journal_id': journal_id.id,
            'date': self.scheduled_date or fields.Date.today(),
            'ref': self.name,
            'line_ids': lines,
            'type': 'entry',
        }
        move = self.env['account.move'].sudo().create(move_vals)
        move.post()
