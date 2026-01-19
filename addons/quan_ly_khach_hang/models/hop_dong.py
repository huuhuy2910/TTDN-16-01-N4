# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class HopDong(models.Model):
    _name = 'hop_dong'
    _description = 'Quản lý hợp đồng khách hàng'
    _rec_name = 'ten_hop_dong'
    _order = 'ngay_ky desc'

    ma_hop_dong = fields.Char("Mã hợp đồng", required=True, copy=False)
    ten_hop_dong = fields.Char("Tên hợp đồng", required=True)
    khach_hang_id = fields.Many2one('khach_hang', string="Khách hàng", required=True, ondelete='cascade')
    
    loai_hop_dong = fields.Selection([
        ('ban_hang', 'Hợp đồng bán hàng'),
        ('dich_vu', 'Hợp đồng dịch vụ'),
        ('thue', 'Hợp đồng thuê'),
        ('hop_tac', 'Hợp đồng hợp tác'),
        ('lao_dong', 'Hợp đồng lao động'),
        ('khac', 'Khác'),
    ], string="Loại hợp đồng", default='dich_vu')
    
    ngay_ky = fields.Date("Ngày ký", required=True, default=fields.Date.today)
    ngay_hieu_luc = fields.Date("Ngày hiệu lực")
    ngay_het_han = fields.Date("Ngày hết hạn")
    
    gia_tri = fields.Float("Giá trị hợp đồng")
    don_vi_tien = fields.Selection([
        ('vnd', 'VND'),
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ], string="Đơn vị tiền", default='vnd')
    
    nhan_vien_phu_trach_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách")
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('hieu_luc', 'Đang hiệu lực'),
        ('het_han', 'Hết hạn'),
        ('huy', 'Đã hủy'),
    ], string="Trạng thái", default='nhap')
    
    mo_ta = fields.Text("Mô tả")
    dieu_khoan = fields.Html("Điều khoản")
    
    # File đính kèm
    file_hop_dong = fields.Binary("File hợp đồng")
    file_hop_dong_name = fields.Char("Tên file")
    
    # Liên kết với tài liệu
    tai_lieu_ids = fields.One2many('tai_lieu', 'hop_dong_id', string="Tài liệu đính kèm")
    
    con_hieu_luc = fields.Boolean(compute="_compute_con_hieu_luc", string="Còn hiệu lực", store=True)
    
    @api.depends('ngay_het_han', 'trang_thai')
    def _compute_con_hieu_luc(self):
        today = date.today()
        for record in self:
            if record.trang_thai == 'hieu_luc' and record.ngay_het_han:
                record.con_hieu_luc = record.ngay_het_han >= today
            else:
                record.con_hieu_luc = record.trang_thai == 'hieu_luc'
    
    _sql_constraints = [
        ('ma_hop_dong_unique', 'unique(ma_hop_dong)', 'Mã hợp đồng phải là duy nhất!')
    ]
    
    # Workflow methods
    def action_submit_for_approval(self):
        """Chuyển trạng thái từ Nháp sang Chờ duyệt"""
        for record in self:
            if record.trang_thai == 'nhap':
                record.trang_thai = 'cho_duyet'
    
    def action_approve(self):
        """Duyệt hợp đồng - chuyển sang Hiệu lực"""
        for record in self:
            if record.trang_thai == 'cho_duyet':
                record.trang_thai = 'hieu_luc'
    
    def action_cancel(self):
        """Hủy hợp đồng"""
        for record in self:
            if record.trang_thai in ['nhap', 'cho_duyet', 'hieu_luc']:
                record.trang_thai = 'huy'
    
    def action_expire(self):
        """Đánh dấu hết hạn (có thể gọi tự động)"""
        for record in self:
            if record.trang_thai == 'hieu_luc':
                record.trang_thai = 'het_han'

    @api.model
    def create(self, vals):
        """Tạo hợp đồng và sinh một văn bản đến (van_ban_den) để ghi nhận hồ sơ.
        Tránh tạo trùng lặp nếu đã tồn tại van_ban_den cho hợp đồng này.
        """
        record = super(HopDong, self).create(vals)
        try:
            van_ban_obj = self.env.get('van_ban_den')
            if van_ban_obj:
                exists = van_ban_obj.search([('hop_dong_id', '=', record.id)], limit=1)
                if not exists:
                    so_vb = 'HD-%s' % (record.ma_hop_dong or record.id)
                    van_ban_obj.create({
                        'so_van_ban_den': so_vb,
                        'ten_van_ban': 'Hợp đồng: %s' % (record.ten_hop_dong or record.ma_hop_dong),
                        'khach_hang_id': record.khach_hang_id.id or False,
                        'hop_dong_id': record.id,
                        'file_van_ban': record.file_hop_dong,
                        'file_van_ban_name': record.file_hop_dong_name,
                        'trang_thai_xu_ly': 'chua_xu_ly',
                    })
        except Exception:
            pass
        return record
