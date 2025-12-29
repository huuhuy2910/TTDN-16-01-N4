# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VanBanDen(models.Model):
    _name = 'van_ban_den'
    _description = 'Văn bản đến'

    so_van_ban = fields.Char("Số văn bản", required=True)
    trich_yeu = fields.Char("Trích yếu", required=True)
    loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản", required=True)
    ngay_den = fields.Date("Ngày đến", default=fields.Date.today)
    ngay_van_ban = fields.Date("Ngày văn bản")
    co_quan_ban_hanh = fields.Char("Cơ quan ban hành")
    nguoi_ky = fields.Char("Người ký")
    so_trang = fields.Integer("Số trang")
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file = fields.Char("Tên file")
    ghi_chu = fields.Text("Ghi chú")
    trang_thai = fields.Selection([
        ('moi', 'Mới'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
        ('luu_tru', 'Lưu trữ')
    ], string="Trạng thái", default='moi', tracking=True)

    def action_dang_xu_ly(self):
        for rec in self:
            rec.trang_thai = 'dang_xu_ly'

    def action_da_xu_ly(self):
        for rec in self:
            rec.trang_thai = 'da_xu_ly'

    def action_luu_tru(self):
        for rec in self:
            rec.trang_thai = 'luu_tru'

    _sql_constraints = [
        ('so_van_ban_unique', 'unique(so_van_ban)', 'Số văn bản đến phải là duy nhất!')
    ]
