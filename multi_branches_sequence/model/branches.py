from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Branch(models.Model):
    _inherit = 'res.branch'

    so_code = fields.Char('Sale Code')
    so_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    so_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_so_seq_number_next',
                                          inverse='_inverse_so_seq_number_next')

    po_code = fields.Char('Purchase Code')
    po_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    po_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_po_seq_number_next',
                                             inverse='_inverse_po_seq_number_next')

    inv_code = fields.Char('Invoice Code')
    inv_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    inv_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_inv_seq_number_next',
                                             inverse='_inverse_inv_seq_number_next')

    bill_code = fields.Char('Bill Code')
    bill_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    bill_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_bill_seq_number_next',
                                             inverse='_inverse_bill_seq_number_next')

    credit_code = fields.Char('Credit Note Code')
    credit_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    credit_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_credit_seq_number_next',
                                               inverse='_inverse_credit_seq_number_next')
    out_receipt_code = fields.Char('Invoice Receipt Code')
    out_receipt_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    out_receipt_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_out_receipt_seq_number_next',
                                                 inverse='_inverse_out_receipt_seq_number_next')

    refund_code = fields.Char('Refund Code')
    refund_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    refund_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_refund_seq_number_next',
                                                 inverse='_inverse_refund_seq_number_next')

    in_receipt_code = fields.Char('Bill Receipt Code')
    in_receipt_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    in_receipt_sequence_number_next = fields.Integer(string='Next Number',
                                                      compute='_compute_in_receipt_seq_number_next',
                                                      inverse='_inverse_in_receipt_seq_number_next')

    cus_code = fields.Char('Customer Payment Code')
    cus_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    cus_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_cus_seq_number_next',
                                                 inverse='_inverse_cus_seq_number_next')

    ven_code = fields.Char('Vendor Payment Code')
    ven_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    ven_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_ven_seq_number_next',
                                                 inverse='_inverse_ven_seq_number_next')

    cusout_code = fields.Char('Customer/Out Payment')
    cusout_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    cusout_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_cusout_seq_number_next',
                                              inverse='_inverse_cusout_seq_number_next')

    venout_code = fields.Char('Vendor/Out Payment')
    venout_sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', required=True, copy=False)
    venout_sequence_number_next = fields.Integer(string='Next Number', compute='_compute_venout_seq_number_next',
                                              inverse='_inverse_venout_seq_number_next')

    @api.depends('so_sequence_id.number_next_actual')
    def _compute_so_seq_number_next(self):
        for branch in self:
            if branch.so_sequence_id:
                sequence = branch.so_sequence_id._get_current_sequence()
                branch.so_sequence_number_next = sequence.number_next_actual
            else:
                branch.so_sequence_number_next = 1

    @api.depends('po_sequence_id.number_next_actual')
    def _compute_po_seq_number_next(self):
        for branch in self:
            if branch.po_sequence_id:
                sequence = branch.po_sequence_id._get_current_sequence()
                branch.po_sequence_number_next = sequence.number_next_actual
            else:
                branch.po_sequence_number_next = 1

    @api.depends('inv_sequence_id.number_next_actual')
    def _compute_inv_seq_number_next(self):
        for branch in self:
            if branch.inv_sequence_id:
                sequence = branch.inv_sequence_id._get_current_sequence()
                branch.inv_sequence_number_next = sequence.number_next_actual
            else:
                branch.inv_sequence_number_next = 1

    @api.depends('bill_sequence_id.number_next_actual')
    def _compute_bill_seq_number_next(self):
        for branch in self:
            if branch.bill_sequence_id:
                sequence = branch.bill_sequence_id._get_current_sequence()
                branch.bill_sequence_number_next = sequence.number_next_actual
            else:
                branch.bill_sequence_number_next = 1

    @api.depends('credit_sequence_id.number_next_actual')
    def _compute_credit_seq_number_next(self):
        for branch in self:
            if branch.credit_sequence_id:
                sequence = branch.credit_sequence_id._get_current_sequence()
                branch.credit_sequence_number_next = sequence.number_next_actual
            else:
                branch.credit_sequence_number_next = 1

    @api.depends('out_receipt_sequence_id.number_next_actual')
    def _compute_out_receipt_seq_number_next(self):
        for branch in self:
            if branch.out_receipt_sequence_id:
                sequence = branch.out_receipt_sequence_id._get_current_sequence()
                branch.out_receipt_sequence_number_next = sequence.number_next_actual
            else:
                branch.out_receipt_sequence_number_next = 1

    @api.depends('refund_sequence_id.number_next_actual')
    def _compute_refund_seq_number_next(self):
        for branch in self:
            if branch.refund_sequence_id:
                sequence = branch.refund_sequence_id._get_current_sequence()
                branch.refund_sequence_number_next = sequence.number_next_actual
            else:
                branch.refund_sequence_number_next = 1

    @api.depends('in_receipt_sequence_id.number_next_actual')
    def _compute_in_receipt_seq_number_next(self):
        for branch in self:
            if branch.in_receipt_sequence_id:
                sequence = branch.in_receipt_sequence_id._get_current_sequence()
                branch.in_receipt_sequence_number_next = sequence.number_next_actual
            else:
                branch.in_receipt_sequence_number_next = 1

    @api.depends('cus_sequence_id.number_next_actual')
    def _compute_cus_seq_number_next(self):
        for branch in self:
            if branch.cus_sequence_id:
                sequence = branch.cus_sequence_id._get_current_sequence()
                branch.cus_sequence_number_next = sequence.number_next_actual
            else:
                branch.cus_sequence_number_next = 1

    @api.depends('cusout_sequence_id.number_next_actual')
    def _compute_cusout_seq_number_next(self):
        for branch in self:
            if branch.cusout_sequence_id:
                sequence = branch.cusout_sequence_id._get_current_sequence()
                branch.cusout_sequence_number_next = sequence.number_next_actual
            else:
                branch.cusout_sequence_number_next = 1

    @api.depends('ven_sequence_id.number_next_actual')
    def _compute_ven_seq_number_next(self):
        for branch in self:
            if branch.ven_sequence_id:
                sequence = branch.ven_sequence_id._get_current_sequence()
                branch.ven_sequence_number_next = sequence.number_next_actual
            else:
                branch.ven_sequence_number_next = 1

    @api.depends('venout_sequence_id.number_next_actual')
    def _compute_venout_seq_number_next(self):
        for branch in self:
            if branch.venout_sequence_id:
                sequence = branch.venout_sequence_id._get_current_sequence()
                branch.venout_sequence_number_next = sequence.number_next_actual
            else:
                branch.venout_sequence_number_next = 1

    def _inverse_so_seq_number_next(self):
        for branch in self:
            if branch.so_sequence_id and branch.so_sequence_number_next:
                sequence = branch.so_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.so_sequence_number_next

    def _inverse_po_seq_number_next(self):
        for branch in self:
            if branch.po_sequence_id and branch.po_sequence_number_next:
                sequence = branch.po_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.po_sequence_number_next

    def _inverse_inv_seq_number_next(self):
        for branch in self:
            if branch.inv_sequence_id and branch.inv_sequence_number_next:
                sequence = branch.inv_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.inv_sequence_number_next

    def _inverse_bill_seq_number_next(self):
        for branch in self:
            if branch.bill_sequence_id and branch.bill_sequence_number_next:
                sequence = branch.bill_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.bill_sequence_number_next

    def _inverse_credit_seq_number_next(self):
        for branch in self:
            if branch.credit_sequence_id and branch.credit_sequence_number_next:
                sequence = branch.credit_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.credit_sequence_number_next

    def _inverse_in_receipt_seq_number_next(self):
        for branch in self:
            if branch.in_receipt_sequence_id and branch.in_receipt_sequence_number_next:
                sequence = branch.in_receipt_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.in_receipt_sequence_number_next

    def _inverse_refund_seq_number_next(self):
        for branch in self:
            if branch.refund_sequence_id and branch.refund_sequence_number_next:
                sequence = branch.refund_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.refund_sequence_number_next

    def _inverse_out_receipt_seq_number_next(self):
        for branch in self:
            if branch.out_receipt_sequence_id and branch.out_receipt_sequence_number_next:
                sequence = branch.out_receipt_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.out_receipt_sequence_number_next

    def _inverse_cus_seq_number_next(self):
        for branch in self:
            if branch.cus_sequence_id and branch.cus_sequence_number_next:
                sequence = branch.cus_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.cus_sequence_number_next

    def _inverse_cusout_seq_number_next(self):
        for branch in self:
            if branch.cusout_sequence_id and branch.cusout_sequence_number_next:
                sequence = branch.cusout_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.cusout_sequence_number_next

    def _inverse_ven_seq_number_next(self):
        for branch in self:
            if branch.ven_sequence_id and branch.ven_sequence_number_next:
                sequence = branch.ven_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.ven_sequence_number_next

    def _inverse_venout_seq_number_next(self):
        for branch in self:
            if branch.venout_sequence_id and branch.venout_sequence_number_next:
                sequence = branch.venout_sequence_id._get_current_sequence()
                sequence.sudo().number_next = branch.venout_sequence_number_next

    @api.model
    def _get_so_sequence_prefix(self, so_code):
        prefix = so_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_po_sequence_prefix(self, po_code):
        prefix = po_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_inv_sequence_prefix(self, inv_code):
        prefix = inv_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_bill_sequence_prefix(self, bill_code):
        prefix = bill_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_credit_sequence_prefix(self, credit_code):
        prefix = credit_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_in_receipt_sequence_prefix(self, in_receipt_code):
        prefix = in_receipt_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_refund_sequence_prefix(self, refund_code):
        prefix = refund_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_out_receipt_sequence_prefix(self, out_receipt_code):
        prefix = out_receipt_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_cus_sequence_prefix(self, cus_code):
        prefix = cus_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_cusout_sequence_prefix(self, cusout_code):
        prefix = cusout_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_ven_sequence_prefix(self, ven_code):
        prefix = ven_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _get_venout_sequence_prefix(self, venout_code):
        prefix = venout_code.upper()
        return prefix + '/%(range_year)s/'

    @api.model
    def _create_so_sequence(self, vals):
        prefix = self._get_so_sequence_prefix(vals['so_code'])
        seq_name = vals['so_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_po_sequence(self, vals):
        prefix = self._get_po_sequence_prefix(vals['po_code'])
        seq_name = vals['po_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_inv_sequence(self, vals):
        prefix = self._get_inv_sequence_prefix(vals['inv_code'])
        seq_name = vals['inv_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_bill_sequence(self, vals):
        prefix = self._get_bill_sequence_prefix(vals['bill_code'])
        seq_name = vals['bill_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_credit_sequence(self, vals):
        prefix = self._get_credit_sequence_prefix(vals['credit_code'])
        seq_name = vals['credit_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_in_receipt_sequence(self, vals):
        prefix = self._get_in_receipt_sequence_prefix(vals['in_receipt_code'])
        seq_name = vals['in_receipt_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_refund_sequence(self, vals):
        prefix = self._get_refund_sequence_prefix(vals['refund_code'])
        seq_name = vals['refund_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_out_receipt_sequence(self, vals):
        prefix = self._get_out_receipt_sequence_prefix(vals['out_receipt_code'])
        seq_name = vals['out_receipt_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_cus_sequence(self, vals):
        prefix = self._get_cus_sequence_prefix(vals['cus_code'])
        seq_name = vals['cus_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_cusout_sequence(self, vals):
        prefix = self._get_cusout_sequence_prefix(vals['cusout_code'])
        seq_name = vals['cusout_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_ven_sequence(self, vals):
        prefix = self._get_ven_sequence_prefix(vals['ven_code'])
        seq_name = vals['ven_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_venout_sequence(self, vals):
        prefix = self._get_venout_sequence_prefix(vals['venout_code'])
        seq_name = vals['venout_code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def create(self, vals):
        if not vals.get('so_sequence_id'):
            vals.update({'so_sequence_id': self.sudo()._create_so_sequence(vals).id})
        if not vals.get('po_sequence_id'):
            vals.update({'po_sequence_id': self.sudo()._create_po_sequence(vals).id})
        if not vals.get('inv_sequence_id'):
            vals.update({'inv_sequence_id': self.sudo()._create_inv_sequence(vals).id})
        if not vals.get('bill_sequence_id'):
            vals.update({'bill_sequence_id': self.sudo()._create_bill_sequence(vals).id})
        if not vals.get('credit_sequence_id'):
            vals.update({'credit_sequence_id': self.sudo()._create_credit_sequence(vals).id})
        if not vals.get('in_receipt_sequence_id'):
            vals.update({'in_receipt_sequence_id': self.sudo()._create_in_receipt_sequence(vals).id})
        if not vals.get('refund_sequence_id'):
            vals.update({'refund_sequence_id': self.sudo()._create_refund_sequence(vals).id})
        if not vals.get('out_receipt_sequence_id'):
            vals.update({'out_receipt_sequence_id': self.sudo()._create_out_receipt_sequence(vals).id})
        if not vals.get('cus_sequence_id'):
            vals.update({'cus_sequence_id': self.sudo()._create_cus_sequence(vals).id})
        if not vals.get('cusout_sequence_id'):
            vals.update({'cusout_sequence_id': self.sudo()._create_cusout_sequence(vals).id})
        if not vals.get('ven_sequence_id'):
            vals.update({'ven_sequence_id': self.sudo()._create_ven_sequence(vals).id})
        if not vals.get('venout_sequence_id'):
            vals.update({'venout_sequence_id': self.sudo()._create_venout_sequence(vals).id})
        branch = super(Branch, self).create(vals)
        return branch



