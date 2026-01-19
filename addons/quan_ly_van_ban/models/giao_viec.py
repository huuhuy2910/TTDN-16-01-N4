# -*- coding: utf-8 -*-
from odoo import models, fields

class GiaoViec(models.Model):
    _name = 'giao_viec'
    _description = 'Deprecated - will be removed'
    
    name = fields.Char("Name")
