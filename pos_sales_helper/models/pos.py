# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    sales_team_id = fields.Many2one(
        'crm.team',
        string="Sales Team",
        copy=False,
        states={
            'draft': [('readonly', False)]
        },
        readonly=True
    )
    sales_man_id = fields.Many2one(
        'hr.employee',
        string="Sales Man",
        copy=False,
        states={
            'draft': [('readonly', False)]
        },
        readonly=True
    )


    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        result.update({
            'sales_team_id': ui_order.get('sales_team_id', False),
            'sales_man_id':  ui_order.get('sales_man_id', False),

        })
        return result

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        vals.update({
            'sales_team_id': self.sales_team_id.id,
            'sales_man_id': self.sales_man_id.id,

        })
        return vals

