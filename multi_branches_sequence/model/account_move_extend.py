from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_sequence(self):
        if self.branch_id:
            self.ensure_one()
            journal = self.journal_id
            branch = self.branch_id
            if self.type in 'entry' or not journal.refund_sequence:
                return journal.sequence_id
            elif self.type in 'out_invoice' or not journal.refund_sequence:
                return branch.inv_sequence_id
            elif self.type in 'out_refund' or not journal.refund_sequence:
                return branch.credit_sequence_id
            elif self.type in 'out_receipt' or not journal.refund_sequence:
                return branch.out_receipt_sequence_id
            elif self.type in 'in_invoice' or not journal.refund_sequence:
                return branch.bill_sequence_id
            elif self.type in 'in_refund' or not journal.refund_sequence:
                return branch.refund_sequence_id
            elif self.type in 'in_receipt' or not journal.refund_sequence:
                return branch.in_receipt_sequence_id
            if not journal.refund_sequence_id:
                return
            return journal.refund_sequence_id
        else:
            self.ensure_one()
            journal = self.journal_id
            if self.type in (
            'entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') or not journal.refund_sequence:
                return journal.sequence_id
            if not journal.refund_sequence_id:
                return
            return journal.refund_sequence_id

