from odoo import models,fields,api

class IssueType(models.Model):

    _name = 'issue.type'
    _description = 'Issue Type'

    name = fields.Char('Issue Type')