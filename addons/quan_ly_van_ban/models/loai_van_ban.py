# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LoaiVanBan(models.Model):
    _name = 'loai_van_ban'
    _description = 'Danh mục loại văn bản'
    _rec_name = 'ten_loai'
    _order = 'ma_loai asc'
    
    ma_loai = fields.Char("Mã loại", required=True, copy=False)
    ten_loai = fields.Char("Tên loại văn bản", required=True)
    mo_ta = fields.Text("Mô tả")
    hoat_dong = fields.Boolean("Hoạt động", default=True)
    
    # Liên kết ngược
    van_ban_den_ids = fields.One2many('van_ban_den', 'loai_van_ban_id', string="Văn bản đến")
    van_ban_di_ids = fields.One2many('van_ban_di', 'loai_van_ban_id', string="Văn bản đi")
    
    _sql_constraints = [
        ('ma_loai_unique', 'unique(ma_loai)', 'Mã loại văn bản đã tồn tại!')
    ]
