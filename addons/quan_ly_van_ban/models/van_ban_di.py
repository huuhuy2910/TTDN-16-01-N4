# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Văn bản đi'

    so_van_ban = fields.Char("Số văn bản", required=True)
    trich_yeu = fields.Char("Trích yếu", required=True)
    loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản", required=True)
    ngay_di = fields.Date("Ngày đi", default=fields.Date.today)
    ngay_van_ban = fields.Date("Ngày văn bản")
    noi_nhan = fields.Char("Nơi nhận")
    nguoi_ky = fields.Char("Người ký")
    so_trang = fields.Integer("Số trang")
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file = fields.Char("Tên file")
    ghi_chu = fields.Text("Ghi chú")
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_gui', 'Đã gửi'),
        ('luu_tru', 'Lưu trữ')
    ], string="Trạng thái", default='nhap', tracking=True)

    def action_chuyen_cho_duyet(self):
        for rec in self:
            rec.trang_thai = 'cho_duyet'

    def action_duyet(self):
        for rec in self:
            rec.trang_thai = 'da_duyet'

    def action_gui(self):
        for rec in self:
            rec.trang_thai = 'da_gui'

    def action_luu_tru(self):
        for rec in self:
            rec.trang_thai = 'luu_tru'

    _sql_constraints = [
        ('so_van_ban_unique', 'unique(so_van_ban)', 'Số văn bản đi phải là duy nhất!')
    ]
