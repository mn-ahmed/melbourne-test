# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class StocksMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        price_unit = super(StocksMove, self)._get_price_unit()

        line = self.purchase_line_id
        if line and self.product_id.id == line.product_id.id:
            if line.discount_type and line.discount_amount:
                price_unit = line.price_unit
                order = line.order_id

                product_qty = 1.0
                if line.discount_type == 'percentage':
                    price_unit = price_unit * (1 - (line.discount_amount or 0.0) / 100.0)
                else:
                    price_unit = (price_unit * product_qty) - (line.discount_amount * product_qty)  # 11.8.2020 THA

                if line.taxes_id:
                    rr = line.taxes_id.with_context(round=False).compute_all(price_unit,
                                                                             currency=line.order_id.currency_id,
                                                                             quantity=1.0)
                    price_unit = rr['total_void']

                if line.product_uom.id != line.product_id.uom_id.id:
                    price_unit *= line.product_uom.factor / line.product_id.uom_id.factor

                if order.currency_id != order.company_id.currency_id:
                    # The date must be today, and not the date of the move since the move move is still
                    # in assigned state. However, the move date is the scheduled date until move is
                    # done, then date of actual move processing. See:
                    # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                    price_unit = order.currency_id._convert(
                        price_unit, order.company_id.currency_id, order.company_id, self.picking_id.scheduled_date,
                        round=False)
        return price_unit

    def _create_in_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_in_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                                     move.product_id.uom_id)
            unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
            if move.product_id.cost_method == 'standard':
                unit_cost = move.product_id.standard_price
            if forced_quantity or valued_quantity:
                if move.purchase_line_id:
                    po_id = move.purchase_line_id.order_id
                    from_currency = move.purchase_line_id.order_id.currency_id
                    to_currency = po_id.company_id.currency_id

                    purchase_cost = move.purchase_line_id.price_subtotal
                    if from_currency != to_currency:
                        purchase_cost = from_currency._convert(
                            move.purchase_line_id.price_subtotal,
                            to_currency,
                            move.purchase_line_id.order_id.company_id,
                            move.picking_id.scheduled_date
                        )
                    unit_cost = purchase_cost / move.purchase_line_id.product_qty
            svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals[
                    'description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_type = fields.Selection([
        ('percent', 'Percentage'),
        ('amount', 'Amount')],
        string='Discount Type',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        default='percent'
    )
    discount_rate = fields.Float(
        string='Global Discount',
        readonly=True,
        states={
        'draft': [('readonly', False)],
        'sent': [('readonly', False)]
        }
    )
    amount_global_discount = fields.Monetary(
        string='Global Discount',
        readonly=True,
        compute='_compute_amount',
        store=True,
        track_visibility='always'
    )
    apply_discount = fields.Boolean(
        compute='verify_discount'
    )
    sales_discount_account_id_id = fields.Integer(
        compute='verify_discount'
    )
    purchase_discount_account_id_id = fields.Integer(
        compute='verify_discount'
    )
    tax_type = fields.Selection(
        selection=[
            ('exclude_tax', "Exclude Tax")
        ],
        string="Tax Payment Type"
    )
    is_tax = fields.Boolean(
        "Is Tax",
        default=False,
    )
    amount_total_line_disc = fields.Monetary(
        string='After Line Discount',
        store=True,
        readonly=True,
        compute='_compute_amount'
    )
    amount_total_after_tax = fields.Monetary(
        string='Total After Tax',
        store=True,
        readonly=True,
        compute='_compute_amount',
        track_visibility='always'
    )
    total_discount_amount = fields.Float(
        'Total Line Discount Amount'
        )#THA 17.9.2020

    @api.depends('company_id.apply_discount')
    def verify_discount(self):
        for rec in self:
            rec.apply_discount = rec.company_id.apply_discount
            rec.sales_discount_account_id_id = rec.company_id.sales_discount_account_id.id
            rec.purchase_discount_account_id_id = rec.company_id.purchase_discount_account_id.id

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'discount_type',
        'discount_rate')
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        for rec in self:
            if not rec.asset_id:
                amount_total_line_disc = 0.0
                amount_untaxed = 0.0
                tmp_price_subtotal = tmp_amount_untaxed = tmp_total = 0.0
                amount_tax = 0.0
                line_discount = 0.0
                total_discount_amount = 0.0#THA 17.9.2020

                #KAP 03.09.2020
                if rec.invoice_filter_type_domain =='purchase':
                    for line in rec.invoice_line_ids:
                        tmp_total = line.price_unit * line.quantity

                        if line.discount_type == 'fixed':
                            line_discount = line.discount_amount*line.quantity
                        else:
                            line_discount = tmp_total *(line.discount_amount/100)

                        tmp_price_subtotal = tmp_total - line_discount
                        total_discount_amount += line_discount
                        if line.tax_ids:
                            for tax in line.tax_ids:
                                if tax.price_include != True:
                                    tmp_price_subtotal = line.price_subtotal
                                    tt= (tmp_price_subtotal *(tax.amount / 100.00))
                                    amount_tax += (line.price_total - line.price_subtotal)#round(tt, 2)
                                    tmp_amount_untaxed += tmp_price_subtotal#round(tmp_price_subtotal, 2)
                                else:
                                    tmp_price_subtotal = tmp_total - line_discount
                                    tx = tmp_price_subtotal /((100+tax.amount ) / tax.amount)
                                    amount_tax += round(tx, 2)# (tmp_price_subtotal /((100+tax.amount ) / tax.amount))
                                    tmp_price_subtotal = tmp_price_subtotal -tx#(tmp_price_subtotal/((100+tax.amount ) / tax.amount))
                                    tmp_amount_untaxed += round(tmp_price_subtotal, 2)
                        else:
                            tmp_amount_untaxed += tmp_price_subtotal
                        line.price_subtotal = tmp_price_subtotal

                elif rec.invoice_filter_type_domain == 'sale':
                    for line in rec.invoice_line_ids:
                        tmp_total = line.price_unit * line.quantity

                        line_discount = 0.0
                        if line.discount_type == 'fixed':
                            line_discount = line.quantity * line.discount_amount
                        else:
                            line_discount = tmp_total * (line.discount_amount / 100)

                        tmp_price_subtotal = tmp_total - line_discount
                        total_discount_amount += line_discount

                        for tax in line.tax_ids:
                            if tax.price_include != True:
                                tx = tmp_price_subtotal * (tax.amount / 100)
                                tmp_price_subtotal = tmp_price_subtotal  # + tx
                                amount_tax += tx
                            else:
                                tx = tmp_price_subtotal / ((100 + tax.amount) / tax.amount)
                                amount_tax += tx
                                tmp_price_subtotal = tmp_price_subtotal - tx

                        tmp_amount_untaxed += tmp_price_subtotal

                rec.amount_untaxed = tmp_amount_untaxed

                amount_total_line_disc = sum(l.price_subtotal for l in rec.invoice_line_ids)
                rec.amount_total_line_disc = tmp_amount_untaxed# -total_line_discount

                rec.total_discount_amount = total_discount_amount#THA 17.9.2020

                rec.amount_tax = amount_tax

                rec.amount_total_after_tax = round(rec.amount_total_line_disc + rec.amount_tax, 2)
                if rec.is_outbound():
                    sign = -1
                else:
                    sign = 1

                amount_total_signed = rec.amount_total
                if rec.company_id:
                    if rec.currency_id != rec.company_id.currency_id:
                        amount_total_signed = rec.currency_id._convert(rec.amount_total, rec.company_id.currency_id, rec.company_id, rec.date)

                rec.amount_total_company_signed = rec.amount_total * sign
                rec.amount_total_signed = amount_total_signed * sign
                if not ('global_tax_rate' in rec):
                    rec.calculate_discount()


    def calculate_discount(self):
        for rec in self:
            if rec.discount_type == "amount":
                rec.amount_global_discount = rec.discount_rate if rec.amount_total_after_tax > 0 else 0
            elif rec.discount_type == "percent":
                if rec.discount_rate != 0.0:
                    rec.amount_global_discount = (rec.amount_total_after_tax ) * rec.discount_rate / 100
                else:
                    rec.amount_global_discount = 0
            elif not rec.discount_type:
                rec.discount_rate = 0
                rec.amount_global_discount = 0
            rec.amount_total = rec.amount_total_after_tax - rec.amount_global_discount
            rec.update_universal_discount()

    @api.constrains('discount_rate')
    def check_discount_value(self):
        if self.discount_type == "percent":
            if self.discount_rate > 100 or self.discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.discount_rate < 0 or self.amount_untaxed < 0:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')

    @api.model
    def _prepare_refund(self,
            invoice, date_invoice=None, date=None,
            description=None, journal_id=None
        ):
        res = super(AccountMove, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id
        )
        res['discount_rate'] = self.discount_rate
        res['discount_type'] = self.discount_type
        return res

    def update_universal_discount(self):
        """This Function Updates the Global Discount through Sale Order"""
        for rec in self:
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Global Discount') == 0)
            terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            other_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))

            different_currency = False
            if rec.currency_id != rec.company_id.currency_id:
                different_currency = True

            if already_exists:
                amount = rec.amount_global_discount
                amount = rec.currency_id._convert(
                    amount, rec.company_id.currency_id, rec.company_id,
                    rec.date or fields.Date.today()
                )

                if rec.sales_discount_account_id_id and (rec.type == "out_invoice" or rec.type == "out_refund") and amount > 0:
                    if rec.type == "out_invoice":
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    if different_currency:
                        if rec.type == "out_refund":
                            already_exists.update({
                                'amount_currency': -1 * rec.amount_global_discount,
                                'currency_id': rec.currency_id.id
                            })
                        else:
                            already_exists.update({
                                'amount_currency': rec.amount_global_discount,
                                'currency_id': rec.currency_id.id
                            })

                if rec.purchase_discount_account_id_id and (rec.type == "in_invoice" or rec.type == "in_refund") and amount > 0:
                    if rec.type == "in_invoice":
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })

                    if different_currency:
                        if rec.type == "in_refund":
                            already_exists.update({
                                'amount_currency':  rec.amount_global_discount,
                                'currency_id': rec.currency_id.id
                            })
                        else:
                            already_exists.update({
                                'amount_currency': -1 * rec.amount_global_discount,
                                'currency_id': rec.currency_id.id
                            })

                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                terms_lines.update({
                    'amount_currency': -total_amount_currency,
                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                    'credit': total_balance > 0.0 and total_balance or 0.0,
                })
            if not already_exists and rec.discount_rate > 0:
                in_draft_mode = self != self._origin
                if not in_draft_mode and rec.type == 'out_invoice':
                    rec._recompute_universal_discount_lines()

    @api.onchange('discount_rate', 'discount_type', 'line_ids')
    def _recompute_universal_discount_lines(self):
        """This Function Create The General Entries for Global Discount"""
        for rec in self:

            different_currency = False
            if rec.currency_id != rec.company_id.currency_id:
                different_currency = True

            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.discount_rate > 0 and rec.type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    m_name = "Global Discount "
                    if rec.discount_type == "amount":
                        m_value = "of amount #" + str(self.discount_rate)
                    elif rec.discount_type == "percent":
                        m_value = " @" + str(self.discount_rate) + "%"
                    else:
                        m_value = ''
                    m_name = m_name + m_value
                    #           ("Invoice No: " + str(self.ids)
                    #            if self._origin.id
                    #            else (self.display_name))
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    already_exists = self.line_ids.filtered(
                                    lambda line: line.name and line.name.find('Global Discount') == 0)
                    if already_exists:
                        amount = self.amount_global_discount
                        amount = rec.currency_id._convert(
                            amount, rec.company_id.currency_id, rec.company_id,
                            rec.date or fields.Date.today()
                        )

                        if self.sales_discount_account_id_id \
                                and (self.type == "out_invoice"
                                     or self.type == "out_refund"):
                            if self.type == "out_invoice":
                                already_exists.update({
                                    'name': m_name,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                already_exists.update({
                                    'name': m_name,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                                if different_currency:
                                    already_exists.update({
                                        'amount_currency': rec.amount_global_discount,
                                        'currency_id': rec.currency_id.id
                                    })

                        if self.purchase_discount_account_id_id\
                                and (self.type == "in_invoice"
                                     or self.type == "in_refund"):
                            if self.type == "in_invoice":
                                already_exists.update({
                                    'name': m_name,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })

                            else:
                                already_exists.update({
                                    'name': m_name,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })

                            if different_currency:
                                if rec.type == "in_refund":
                                    already_exists.update({
                                        'amount_currency': rec.amount_global_discount,
                                        'currency_id': rec.currency_id.id
                                    })
                                else:
                                    already_exists.update({
                                        'amount_currency': -1 * rec.amount_global_discount,
                                        'currency_id': rec.currency_id.id
                                    })
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or\
                                        self.env['account.move.line'].create

                        if self.sales_discount_account_id_id \
                                and (self.type == "out_invoice"
                                     or self.type == "out_refund"):
                            amount = self.amount_global_discount
                            amount = rec.currency_id._convert(
                                amount, rec.company_id.currency_id, rec.company_id,
                                rec.date or fields.Date.today()
                            )

                            dict = {
                                    'move_name': self.name,
                                    'name': m_name,
                                    'price_unit': self.amount_global_discount,
                                    'quantity': 1,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                    'account_id': self.sales_discount_account_id_id,
                                    'move_id': self._origin,
                                    'date': self.date,
                                    'exclude_from_invoice_tab': True,
                                    'partner_id': terms_lines.partner_id.id,
                                    'company_id': terms_lines.company_id.id,
                                    'company_currency_id': terms_lines.company_currency_id.id,
                                    }
                            if different_currency:
                                dict.update({
                                    'amount_currency': rec.amount_global_discount,
                                    'currency_id': rec.currency_id.id
                                })
                            if self.type == "out_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Global Discount') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    'price_unit': 0.0,
                                    'debit': 0.0,
                                    'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]

                        if self.purchase_discount_account_id_id\
                                and (self.type == "in_invoice"
                                     or self.type == "in_refund"):
                            amount = self.amount_global_discount
                            amount = rec.currency_id._convert(
                                amount, rec.company_id.currency_id, rec.company_id,
                                rec.date or fields.Date.today()
                            )

                            dict = {
                                    'move_name': self.name,
                                    'name': m_name,
                                    'price_unit': self.amount_global_discount,
                                    'quantity': 1,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                    'account_id': self.purchase_discount_account_id_id,
                                    'move_id': self.id,
                                    'date': self.date,
                                    'exclude_from_invoice_tab': True,
                                    'partner_id': terms_lines.partner_id.id,
                                    'company_id': terms_lines.company_id.id,
                                    'company_currency_id': terms_lines.company_currency_id.id,
                            }

                            if self.type == "in_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            if different_currency:
                                if rec.type == "in_refund":
                                    already_exists.update({
                                        'amount_currency': rec.amount_global_discount,
                                        'currency_id': rec.currency_id.id
                                    })
                                else:
                                    already_exists.update({
                                        'amount_currency': -1 * rec.amount_global_discount,
                                        'currency_id': rec.currency_id.id
                                    })

                            self.line_ids += create_method(dict)
                            # updation of invoice line id
                            duplicate_id = self.invoice_line_ids.filtered(
                                lambda line: line.name and line.name.find('Global Discount') == 0)
                            self.invoice_line_ids = self.invoice_line_ids - duplicate_id

                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                                    'amount_currency': -total_amount_currency,
                                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                                    'credit': total_balance > 0.0 and total_balance or 0.0,
                                })
                    else:
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        already_exists = self.line_ids.filtered(
                            lambda line: line.name and line.name.find('Global Discount') == 0)
                        total_balance = sum(other_lines.mapped('balance')) + amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                        }
                        dict2 = {
                                'debit': total_balance < 0.0 and -total_balance or 0.0,
                                'credit': total_balance > 0.0 and total_balance or 0.0,
                                }
                        self.line_ids = [(1, already_exists.id, dict1), (1, terms_lines.id, dict2)]
                        print()

            elif self.discount_rate <= 0:
                already_exists = self.line_ids.filtered(
                    lambda line: line.name and line.name.find('Global Discount') == 0)
                if already_exists:
                    self.line_ids -= already_exists
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    other_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        ''' Load from either an old purchase order, either an old vendor bill.

        When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
        * If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
        * If it's a purchase order, 'purchase_id' is set and this method will load lines.

        /!\ All this not-stored fields must be empty at the end of this function.
        '''
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False

        if not self.purchase_id:
            return

        # Copy partner.
        self.partner_id = self.purchase_id.partner_id
        self.fiscal_position_id = self.purchase_id.fiscal_position_id
        self.invoice_payment_term_id = self.purchase_id.payment_term_id
        self.currency_id = self.purchase_id.currency_id

        self.discount_type = self.purchase_id.discount_type
        self.discount_rate = self.purchase_id.discount_rate

        # self.amount_untaxed = self.purchase_id.amount_untaxed
        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        for line in po_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line.onchange_discount_type()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = set(self.line_ids.mapped('purchase_line_id.order_id.partner_ref'))
        refs = [ref for ref in refs if ref]
        self.ref = ','.join(refs)

        # Compute _invoice_payment_ref.
        if len(refs) == 1:
            self._invoice_payment_ref = refs[0]

        self.purchase_id = False
        self._onchange_currency()
        self.invoice_partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]


    def _recompute_tax_lines_dummy(self, recompute_tax_base_amount=False):
        ''' Compute the dynamic tax lines of the journal entry.

        :param lines_map: The line_ids dispatched by type containing:
            * base_lines: The lines having a tax_ids set.
            * tax_lines: The lines having a tax_line_id set.
            * terms_lines: The lines generated by the payment terms of the invoice.
            * rounding_lines: The cash rounding lines of the invoice.
        '''
        self.ensure_one()
        # if not self.apply_discount or self.type not in ('in_invoice', 'in_refund'):
        #     return super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                if base_line.currency_id:
                    price_unit_foreign_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                    price_unit_comp_curr = base_line.currency_id._convert(price_unit_foreign_curr, move.company_id.currency_id, move.company_id, move.date)
                else:
                    price_unit_foreign_curr = 0.0
                    price_unit_comp_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                tax_type = 'sale' if move.type.startswith('out_') else 'purchase'
                is_refund = move.type in ('out_refund', 'in_refund')
            else:
                handle_price_include = False
                quantity = 1.0
                price_unit_foreign_curr = base_line.amount_currency
                price_unit_comp_curr = base_line.balance
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)

            line_discount = 0
            tmp_total = base_line.price_unit * base_line.quantity
            if base_line.discount_type == 'fixed':
                line_discount = base_line.quantity * base_line.discount_amount
            else:
                line_discount = ((base_line.price_unit * base_line.discount_amount) / 100.0) * base_line.quantity

            tmp_price_subtotal = tmp_total - line_discount

            balance_taxes_res = base_line.tax_ids._origin.compute_all(
                tmp_price_subtotal,
                currency=base_line.company_currency_id,
                quantity=1,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            if move.type == 'entry':
                repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
                if tags_need_inversion:
                    balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                    for tax_res in balance_taxes_res['taxes']:
                        tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            if base_line.currency_id:
                # Multi-currencies mode: Taxes are computed both in company's currency / foreign currency.
                amount_currency_taxes_res = base_line.tax_ids._origin.compute_all(
                    price_unit_foreign_curr,
                    currency=base_line.currency_id,
                    quantity=quantity,
                    product=base_line.product_id,
                    partner=base_line.partner_id,
                    is_refund=self.type in ('out_refund', 'in_refund'),
                    handle_price_include=handle_price_include,
                )

                if move.type == 'entry':
                    repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                    repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                    tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
                    if tags_need_inversion:
                        balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                        for tax_res in balance_taxes_res['taxes']:
                            tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

                for b_tax_res, ac_tax_res in zip(balance_taxes_res['taxes'], amount_currency_taxes_res['taxes']):
                    tax = self.env['account.tax'].browse(b_tax_res['id'])
                    b_tax_res['amount_currency'] = ac_tax_res['amount']

                    # A tax having a fixed amount must be converted into the company currency when dealing with a
                    # foreign currency.
                    if tax.amount_type == 'fixed':
                        b_tax_res['amount'] = base_line.currency_id._convert(b_tax_res['amount'], move.company_id.currency_id, move.company_id, move.date)

            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            line.tag_ids = compute_all_vals['base_tags']

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['balance'] += tax_vals['amount']
                taxes_map_entry['amount_currency'] += tax_vals.get('amount_currency', 0.0)
                taxes_map_entry['tax_base_amount'] += tax_vals['base']
                taxes_map_entry['grouping_dict'] = grouping_dict
            line.tax_exigible = tax_exigible

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # Don't create tax lines with zero balance.
            if self.currency_id.is_zero(taxes_map_entry['balance']) and self.currency_id.is_zero(taxes_map_entry['amount_currency']):
                taxes_map_entry['grouping_dict'] = False

            tax_line = taxes_map_entry['tax_line']
            tax_base_amount = -taxes_map_entry['tax_base_amount'] if self.is_inbound() else taxes_map_entry['tax_base_amount']

            if not tax_line and not taxes_map_entry['grouping_dict']:
                continue
            elif tax_line and recompute_tax_base_amount:
                tax_line.tax_base_amount = tax_base_amount
            elif tax_line and not taxes_map_entry['grouping_dict']:
                # The tax line is no longer used, drop it.
                self.line_ids -= tax_line
            elif tax_line:
                tax_line.update({
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                })
            else:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                tax_line = create_method({
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                tax_line._onchange_amount_currency()
                tax_line._onchange_balance()



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_type = fields.Selection(
        selection=[
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed')
        ],
        default="fixed",
    )
    discount_amount = fields.Float(string="Discount")
    discount = fields.Float(digits=(16, 7))

    @api.onchange(
        'discount_type', 'discount_amount',
        'price_unit', 'quantity',
    )
    def onchange_discount_type(self):
        if self._context.get ('default_type') in ['out_invoice', 'out_refund']:
            if self.discount_type == 'fixed':
                price_unit = self.price_unit
                price_unit = str(price_unit) + '000'

                discount_amount = self.discount_amount
                discount_amount = str(discount_amount) + '000'

                quantity = self.quantity
                quantity = str(quantity) + '000'

                line_discount = (float(discount_amount) * float(quantity))
                line_discount = str(line_discount) + '000'

                if float(price_unit) and float(quantity):

                    discount = (
                                       100 * float(line_discount)
                               ) / (float(price_unit) * float(quantity))
                    self.discount = discount
            else:
                self.discount = self.discount_amount
        elif self._context.get ('default_type') in ['in_invoice', 'in_refund']:
            if self.discount_type == 'fixed':
                discount = 0.0
                if self.price_unit:
                    discount = (100 * self.discount_amount) / self.price_unit
                self.discount = discount
            else:
                self.discount = self.discount_amount


    @api.onchange(
        'quantity', 'discount', 'price_unit',
        'tax_ids', 'discount_amount', 'discount_type',
    )
    def _onchange_price_subtotal(self):
        return super(AccountMoveLine, self)._onchange_price_subtotal()

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for line in self:

            line.debit = round(line.debit, 2)
            line.credit = round(line.credit, 2)
            line.balance = line.debit - line.credit
