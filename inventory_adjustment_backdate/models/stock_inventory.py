# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

import pytz
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class StockInv(models.Model):
    _inherit = "stock.inventory"

    accounting_date = fields.Date(
        'Accounting Date', default=fields.Date.context_today,
        help="Date at which the accounting entries will be created"
             " in case of automated inventory valuation."
             " If empty, the inventory date will be used.")

    date = fields.Datetime(
        states={
            'draft': [('readonly', False)],
        },
    )

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            local_tz_st = pytz.timezone(self.env.user.tz or 'UTC')
            scheduled_date_only = self.date
            start_d = scheduled_date_only.replace(tzinfo=pytz.utc).astimezone(local_tz_st)
            start_date = datetime.strftime(start_d, DEFAULT_SERVER_DATETIME_FORMAT)
            scheduled_date_only = datetime.strptime(
                start_date, '%Y-%m-%d %H:%M:%S'
            )
            date = scheduled_date_only.date()
            self.accounting_date = date

    # @api.model
    # def create(self, vals):
    #     inv = super(StockInv, self).create(vals)
    #     if inv.date:
    #         local_tz_st = pytz.timezone(self.env.user.tz or 'UTC')
    #         scheduled_date_only = inv.date
    #         start_d = scheduled_date_only.replace(tzinfo=pytz.utc).astimezone(local_tz_st)
    #         start_date = datetime.strftime(start_d, DEFAULT_SERVER_DATETIME_FORMAT)
    #         scheduled_date_only = datetime.strptime(
    #             start_date, '%Y-%m-%d %H:%M:%S'
    #         )
    #         date = scheduled_date_only.date()
    #         if inv.accounting_date != date:
    #             raise UserError(
    #                 _('Inventory Date and Accounting Date must be same!')
    #             )
    #     return inv
    #
    # def write(self, vals):
    #     res = super(StockInv, self).write(vals)
    #     if vals.get('date', False):
    #         for inv in self:
    #             if inv.date:
    #                 local_tz_st = pytz.timezone(self.env.user.tz or 'UTC')
    #                 scheduled_date_only = inv.date
    #                 start_d = scheduled_date_only.replace(tzinfo=pytz.utc).astimezone(local_tz_st)
    #                 start_date = datetime.strftime(start_d, DEFAULT_SERVER_DATETIME_FORMAT)
    #                 scheduled_date_only = datetime.strptime(
    #                     start_date, '%Y-%m-%d %H:%M:%S'
    #                 )
    #                 date = scheduled_date_only.date()
    #                 if inv.accounting_date != date:
    #                     raise UserError(
    #                         _('Inventory Date and Accounting Date must be same!')
    #                     )
    #     return res

    def action_start(self):
        for inventory in self:
            if inventory.state != 'draft':
                continue
            vals = {
                'state': 'confirm',
                'date': self.accounting_date,
            }
            if not inventory.line_ids and not inventory.start_empty:
                self.env['stock.inventory.line'].create(inventory._get_inventory_lines_values())
            inventory.write(vals)

    def action_validate(self):
        ctx = self._context.copy()
        ctx.update({'inventory_date': self.date})

        user = self.env.user
        current_date = fields.Date.today()
        self_date = self.accounting_date

        if  (not user.allow_back_date and not user.allow_current_date and not user.allow_future_date):
            raise UserError(
                _('You are not allow to do back date transaction')
            ) 
        if self_date == current_date:
            if not user.allow_current_date:
                raise UserError(
                    _('You are not allow to do current date transaction')
                )

        elif self_date < current_date:
            if user.allow_back_date and user.back_date_limit:
                limit_date = current_date - relativedelta(days=user.back_date_limit)
                if self_date < limit_date:
                    raise UserError(
                        _('You are only allow to do transaction up to %s days back!' %(
                            user.back_date_limit
                            )
                        )
                    )
            else:
                raise UserError(
                    _('You are not allow to do back date transaction')
                )
        elif self_date > current_date:
            if not user.allow_future_date:
                raise UserError(
                    _('You are not allow to do future date transaction')
                )
        return super(StockInv, self.with_context(ctx, force_period_date=self.accounting_date)).action_validate()

    def post_inventory(self):
        ctx = self._context.copy()
        ctx.update({'inventory_date': self.date})

        user = self.env.user
        current_date = fields.Date.today()
        self_date = self.accounting_date

        if (not user.allow_back_date and not user.allow_current_date and not user.allow_future_date):
            raise UserError(
                _('You are not allow to do back date transaction')
            ) 
        
        if self_date == current_date:
            if not user.allow_current_date:
                raise UserError(
                    _('You are not allow to do current date transaction')
                )        
        elif self_date < current_date:
            if user.allow_back_date and user.back_date_limit:
                limit_date = current_date - relativedelta(days=user.back_date_limit)
                if limit_date < self_date:
                    raise UserError(
                        _('You are only allow to do transaction up to %s days back!' %(
                            user.back_date_limit
                            )
                        )
                    )
            else:
                raise UserError(
                    _('You are not allow to do back date transaction')
                )
        elif self_date > current_jdate:
            if not user.allow_future_date:
                raise UserError(
                    _('You are not allow to do future date transaction')
                )
        return super(StockInv, self.with_context(ctx, force_period_date=self.accounting_date)).post_inventory()

    def action_view_related_move_lines(self):
        self.ensure_one()
        for res in self.move_ids:
            res.date = self.accounting_date
            res.move_line_ids.date = self.accounting_date
        return super(StockInv, self).action_view_related_move_lines()


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.onchange('product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'partner_id', 'package_id')
    def _onchange_quantity_context(self):
        product_qty = False
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
        if self.product_id and self.location_id and self.product_id.uom_id.category_id == self.product_uom_id.category_id:  # TDE FIXME: last part added because crash

            ctx = self._context.copy()

            if self.inventory_id.date:
                ctx.update({'inventory_date': self.inventory_id.date})

            theoretical_qty = self.product_id.with_context(ctx).get_theoretical_quantity(
                self.product_id.id,
                self.location_id.id,
                lot_id=self.prod_lot_id.id,
                package_id=self.package_id.id,
                owner_id=self.partner_id.id,
                to_uom=self.product_uom_id.id,
            )
        else:
            theoretical_qty = 0
        # Sanity check on the lot.
        if self.prod_lot_id:
            if self.product_id.tracking == 'none' or self.product_id != self.prod_lot_id.product_id:
                self.prod_lot_id = False

        if self.prod_lot_id and self.product_id.tracking == 'serial':
            # We force `product_qty` to 1 for SN tracked product because it's
            # the only relevant value aside 0 for this kind of product.
            self.product_qty = 1
        elif self.product_id and float_compare(self.product_qty, self.theoretical_qty,
                                               precision_rounding=self.product_uom_id.rounding) == 0:
            # We update `product_qty` only if it equals to `theoretical_qty` to
            # avoid to reset quantity when user manually set it.
            self.product_qty = theoretical_qty
        self.theoretical_qty = theoretical_qty

    def _get_move_values(
            self, qty, location_id, location_dest_id, out
    ):  # 24/09/2019

        ctx = self._context.copy()
        ctx.update(my_test=self.inventory_id.date)

        vals = super(
            InventoryLine, self.with_context(ctx)
        )._get_move_values(
            qty, location_id, location_dest_id, out
        )
        vals.update({
            'date': self.inventory_id.date
        })
        if vals.get('move_line_ids', []):
            if len(vals['move_line_ids'][0]) == 3:
                if isinstance(vals['move_line_ids'][0][2], dict):
                    vals['move_line_ids'][0][2].update({
                        'date': self.inventory_id.date
                    })
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """ Override to handle the case we create inventory line without
        `theoretical_qty` because this field is usually computed, but in some
        case (typicaly in tests), we create inventory line without trigger the
        onchange, so in this case, we set `theoretical_qty` depending of the
        product's theoretical quantity.
        Handles the same problem with `product_uom_id` as this field is normally
        set in an onchange of `product_id`.
        Finally, this override checks we don't try to create a duplicated line.
        """
        res = super(InventoryLine, self).create(vals_list)
        for inv in res:
            ctx = self._context.copy()
            if inv.inventory_id.date:
                ctx.update({'inventory_date': inv.inventory_id.date})
                theoretical_qty = self.env['product.product'].with_context(ctx).get_theoretical_quantity(
                    inv.product_id.id,
                    inv.location_id.id,
                    lot_id=inv.prod_lot_id.id,
                    package_id=inv.package_id.id,
                    owner_id=inv.partner_id.id,
                    to_uom=inv.product_uom_id.id,
                )
                inv.theoretical_qty = theoretical_qty
        return res


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def get_theoretical_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None,
                                 to_uom=None):
        if not self._context.get('inventory_date', False):
            return super(Product, self).get_theoretical_quantity(product_id, location_id, lot_id, package_id, owner_id,
                                                                 to_uom)

        product_id = self.env['product.product'].browse(product_id)
        product_id.check_access_rights('read')
        product_id.check_access_rule('read')

        location_id = self.env['stock.location'].browse(location_id)
        lot_id = self.env['stock.production.lot'].browse(lot_id)
        package_id = self.env['stock.quant.package'].browse(package_id)
        owner_id = self.env['res.partner'].browse(owner_id)
        to_uom = self.env['uom.uom'].browse(to_uom)
        quants = self.env['stock.quant']._gather(product_id, location_id, lot_id=lot_id, package_id=package_id,
                                                 owner_id=owner_id, strict=True)

        theoretical_quantity = sum([quant.quantity for quant in quants])
        if self._context.get('inventory_date', False):
            move_lines = self.env['stock.move.line'].search([
                ('product_id', '=', product_id.id),
                '|',
                ('location_id', '=', location_id.id),
                ('location_dest_id', '=', location_id.id),
                ('lot_id', '=', lot_id.id),
                '|',
                ('package_id', '=', package_id.id),
                ('result_package_id', '=', package_id.id),
                ('date', '<=', self._context['inventory_date'])
            ])
            move_qty = 0.0
            for l in move_lines:
                if l.location_id.id == location_id.id:
                    move_qty -= l.qty_done
                else:
                    move_qty += l.qty_done

            theoretical_quantity = move_qty
        if to_uom and product_id.uom_id != to_uom:
            theoretical_quantity = product_id.uom_id._compute_quantity(theoretical_quantity, to_uom)
        return theoretical_quantity