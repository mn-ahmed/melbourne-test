from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    sales_man_id = fields.Many2one(
        'hr.employee',
        string="Salesman",
        copy=False,
        track_visibility='onchange'
    )
    sale_by = fields.Many2one('hr.employee', string="Sales Person", compute='_get_sale_by', readonly=False, store=True)
    contact_id = fields.Char(string='Contact Name')
    contact_phone = fields.Char('Contact Phone')
    contact_address = fields.Char('Contact Address')
    accept_person = fields.Char(string='Accept Person')

    so_name = fields.Char(string='SO Number', compute='_get_so_name')
    picking_number = fields.Char(string='Picking Number', compute='_get_so_name')

    def _get_so_name(self):
        for rec in self:
            if rec.invoice_origin is not None:
                rec.so_name = self.env['sale.order'].search(
                    [('name', '=', rec.invoice_origin)]).name
                rec.picking_number = self.env['sale.order'].search(
                    [('name', '=', rec.invoice_origin)]).do_name
            else:
                rec.so_name = rec.picking_number = False


    def _get_sale_by(self):
        for rec in self:

            if rec.invoice_origin is not None:
                rec.sale_by = self.env['sale.order'].search(
                    [('name', '=', rec.invoice_origin)]).sale_by


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        if self.partner_type == 'customer':
            return {'domain': {'partner_id': [('customer','=',True)]}}

        else:
            return {'domain': {'partner_id': [('supplier','=',True)]}}

