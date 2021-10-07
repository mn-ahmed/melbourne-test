from odoo import models, fields, api, _


class CountryState(models.Model):
    _inherit = 'res.country.state'

    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', copy=False)
    sequence_number_next = fields.Integer(string='Next Number', compute='_compute_seq_number_next', inverse='_inverse_seq_number_next')

    @api.depends('sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        for state in self:
            if state.sequence_id:
                sequence = state.sequence_id._get_current_sequence()
                state.sequence_number_next = sequence.number_next_actual
            else:
                state.sequence_number_next = 1

    def _inverse_seq_number_next(self):
        for state in self:
            if state.sequence_id and state.sequence_number_next:
                sequence = state.sequence_id._get_current_sequence()
                sequence.sudo().number_next = state.sequence_number_next

    @api.model
    def _get_sequence_prefix(self, code):
        prefix = code.upper()
        return prefix

    @api.model
    def _create_sequence(self, vals):
        prefix = self._get_sequence_prefix(vals['code'])
        seq_name = vals['code']
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
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        state = super(CountryState, self).create(vals)
        return state

