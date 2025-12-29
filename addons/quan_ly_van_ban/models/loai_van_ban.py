# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LoaiVanBan(models.Model):
    _name = 'loai_van_ban'
    _description = 'Loại văn bản'

    ma_loai = fields.Char("Mã loại", required=True)
    ten_loai = fields.Char("Tên loại văn bản", required=True)
    mo_ta = fields.Text("Mô tả")
    active = fields.Boolean("Hoạt động", default=True)

    van_ban_den_ids = fields.One2many('van_ban_den', 'loai_van_ban_id', string="Văn bản đến")
    van_ban_di_ids = fields.One2many('van_ban_di', 'loai_van_ban_id', string="Văn bản đi")

    _sql_constraints = [
        ('ma_loai_unique', 'unique(ma_loai)', 'Mã loại văn bản phải là duy nhất!')
    ]
