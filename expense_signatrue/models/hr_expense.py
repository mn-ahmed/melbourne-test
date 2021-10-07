from odoo import api, fields, models, _
import datetime

class HrExpenseSheet(models.Model):

    _inherit = "hr.expense.sheet"

    first_signature = fields.Binary(string='First approval', attachment=True)
    first_date = fields.Datetime(string='First approval Date', help='First signature approved date', copy=False)
    second_signature = fields.Binary(string='Second approval', attachment=True)
    second_date = fields.Datetime(string='Second approval Date', help='Second signature approved date', copy=False)

    def first_approve_expense_sheets(self):
        res = super(HrExpenseSheet, self).first_approve_expense_sheets()
        self.first_signature = self.env.user.user_signature
        self.first_date = datetime.datetime.now()
        return res

    def approve_expense_sheets(self):
        res = super(HrExpenseSheet, self).approve_expense_sheets()
        self.second_signature = self.env.user.user_signature
        self.second_date = datetime.datetime.now()
        return res



