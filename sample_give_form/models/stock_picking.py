from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sample_id = fields.Many2one(
        'sample.give',"Sample StockPicking Id",
        index=True, ondelete='cascade')
    mr_no = fields.Char(string='MR No',track_visibility='always')
    sale_person = fields.Many2one('res.users',string='Sale By', track_visibility='always',default=lambda self:self.env.user.id)
    staff_name = fields.Many2one('res.users',string='Staff Name',track_visibility='always',default=lambda self:self.env.user)
    sample_give_date = fields.Date(string='Sample Date',default=fields.Date.today(),track_visibility='always')
    return_date = fields.Date(string='To be Return Date',default=fields.Date.today(),track_visibility='always')
    # KMH (1.9.2020)
    transfer_type = fields.Selection([
        ('normal', 'Others'),
        ('sale', 'Sale'),
        ('sale_return', 'Sale Return'),
        ('purchase', 'Purchase'),
        ('purchase_return', 'Purchase Return'),
        ('sample', 'Sample'),
        ('sample_return', 'Sample Return'),
        ('damage_receipt','Damage Return'),
        ('damage_delivery','Damage Change'),]
        ,string="Transfer Type",Store=True,Copy=False,default='normal')
    issued_date = fields.Date(string='Received Date',default=fields.Date.today(),track_visibility='always')

    sample_remark = fields.Text(string="Sample Remark")

    team_id = fields.Many2one('crm.team', 'Sales Team')
    sale_by = fields.Many2one('hr.employee','Sales Person', track_visibility='always')
    customer_name = fields.Many2one('res.partner', string='Customer Name')
    phone = fields.Char(sting='phone')
    contact_id = fields.Char(string='Contact Name', compute='_get_contact_name')
    description = fields.Text("Description")

    def _get_contact_name(self):

        self.contact_id = False
        if self.partner_id:
            query = """select name,phone from res_partner rp WHERE rp.parent_id=""" + str(
                self.partner_id.id) + """ AND rp.type='delivery';"""
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()

            for val in result:
                self.contact_id = val['name']
                self.phone = val['phone']

    @api.onchange('state')
    def onchange_state(self):
        if self.transfer_type == 'sample' and self.state == 'done':
            self.sample_id.state = 'delivered'
        elif self.transfer_type == 'sample_return' and self.state == 'done':
            self.sample_id.state = 'returned'

    # def action_done(self):
    #     res = super(StockPicking,self).action_done()
    #     if self.sample_id:
    #         sample_obj = self.env['sample.give'].search([('id','=',self.sample_id.id)])
    #         for line in self.move_line_ids_without_package:
    #             for l in sample_obj.product_line:
    #                 if line.product_id == l.product_id:
    #                     if self.transfer_type == 'sample':
    #                         l.deliver_qty += line.qty_done
    #                         l.balance_qty = l.deliver_qty - l.return_qty
    #                     elif self.transfer_type == 'sample_return':
    #                         l.return_qty += line.qty_done
    #                         l.balance_qty = l.deliver_qty - l.return_qty
    #     return res