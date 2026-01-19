# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta

class BaoGia(models.Model):
    _name = 'bao_gia'
    _description = 'Quản lý báo giá'
    _rec_name = 'ten_bao_gia'
    _order = 'ngay_tao desc'

    ma_bao_gia = fields.Char("Mã báo giá", required=True, copy=False)
    ten_bao_gia = fields.Char("Tên báo giá", required=True)
    khach_hang_id = fields.Many2one('khach_hang', string="Khách hàng", required=True, ondelete='cascade')
    
    ngay_tao = fields.Date("Ngày tạo", required=True, default=fields.Date.today)
    ngay_hieu_luc = fields.Date("Hiệu lực đến", default=lambda self: date.today() + timedelta(days=30))
    
    tong_gia_tri = fields.Float("Tổng giá trị")
    don_vi_tien = fields.Selection([
        ('vnd', 'VND'),
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ], string="Đơn vị tiền", default='vnd')
    
    nhan_vien_lap_id = fields.Many2one('nhan_vien', string="Nhân viên lập")
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('gui_khach', 'Đã gửi khách'),
        ('khach_dong_y', 'Khách đồng ý'),
        ('khach_tu_choi', 'Khách từ chối'),
        ('het_han', 'Hết hạn'),
    ], string="Trạng thái", default='nhap')
    
    noi_dung = fields.Html("Nội dung báo giá")
    ghi_chu = fields.Text("Ghi chú")
    
    # File đính kèm
    file_bao_gia = fields.Binary("File báo giá")
    file_bao_gia_name = fields.Char("Tên file")
    
    # Quan hệ với hợp đồng (nếu báo giá được chấp nhận)
    hop_dong_id = fields.Many2one('hop_dong', string="Hợp đồng liên quan")
    
    _sql_constraints = [
        ('ma_bao_gia_unique', 'unique(ma_bao_gia)', 'Mã báo giá phải là duy nhất!')
    ]
    
    # Workflow methods
    def action_send_to_customer(self):
        """Gửi báo giá cho khách hàng"""
        for record in self:
            if record.trang_thai == 'nhap':
                record.trang_thai = 'gui_khach'
    
    def action_customer_approve(self):
        """Khách hàng đồng ý báo giá"""
        for record in self:
            if record.trang_thai == 'gui_khach':
                record.trang_thai = 'khach_dong_y'
    
    def action_customer_reject(self):
        """Khách hàng từ chối báo giá"""
        for record in self:
            if record.trang_thai == 'gui_khach':
                record.trang_thai = 'khach_tu_choi'
    
    def action_expire(self):
        """Báo giá hết hạn"""
        for record in self:
            if record.trang_thai in ['nhap', 'gui_khach']:
                record.trang_thai = 'het_han'

    @api.model
    def create(self, vals):
        """Tạo báo giá và sinh một văn bản đến (van_ban_den) để ghi nhận hồ sơ.
        Tránh tạo trùng lặp nếu đã tồn tại van_ban_den cho báo giá này.
        """
        record = super(BaoGia, self).create(vals)
        try:
            van_ban_obj = self.env.get('van_ban_den')
            if van_ban_obj:
                exists = van_ban_obj.search([('bao_gia_id', '=', record.id)], limit=1)
                if not exists:
                    so_vb = 'BG-%s' % (record.ma_bao_gia or record.id)
                    van_ban_obj.create({
                        'so_van_ban_den': so_vb,
                        'ten_van_ban': 'Báo giá: %s' % (record.ten_bao_gia or record.ma_bao_gia),
                        'khach_hang_id': record.khach_hang_id.id or False,
                        'bao_gia_id': record.id,
                        'file_van_ban': record.file_bao_gia,
                        'file_van_ban_name': record.file_bao_gia_name,
                        'trang_thai_xu_ly': 'chua_xu_ly',
                    })
        except Exception:
            pass
        return record
