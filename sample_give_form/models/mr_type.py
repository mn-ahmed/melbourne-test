# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrType(models.Model):
	_name = 'mr.type'
	_description = 'Mr Type'

	name = fields.Char("Name")