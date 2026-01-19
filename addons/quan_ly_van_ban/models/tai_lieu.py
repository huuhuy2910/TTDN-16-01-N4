# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaiLieu(models.Model):
    _name = 'tai_lieu'
    _description = 'Quản lý tài liệu số hóa'
    _rec_name = 'ten_tai_lieu'
    _order = 'ngay_tao desc'

    ma_tai_lieu = fields.Char("Mã tài liệu", required=True, copy=False)
    ten_tai_lieu = fields.Char("Tên tài liệu", required=True)
    
    loai_tai_lieu = fields.Selection([
        ('hop_dong', 'Hợp đồng'),
        ('bao_gia', 'Báo giá'),
        ('phap_ly', 'Tài liệu pháp lý'),
        ('ky_thuat', 'Tài liệu kỹ thuật'),
        ('tai_chinh', 'Tài liệu tài chính'),
        ('chung_chi', 'Chứng chỉ/Giấy phép'),
        ('bien_ban', 'Biên bản'),
        ('khac', 'Khác'),
    ], string="Loại tài liệu", default='khac')
    
    # Liên kết với khách hàng hoặc hợp đồng
    khach_hang_id = fields.Many2one('khach_hang', string="Khách hàng", ondelete='cascade')
    hop_dong_id = fields.Many2one('hop_dong', string="Hợp đồng liên quan", ondelete='set null')
    
    ngay_tao = fields.Date("Ngày tạo", default=fields.Date.today)
    ngay_hieu_luc = fields.Date("Ngày hiệu lực")
    ngay_het_han = fields.Date("Ngày hết hạn")
    
    mo_ta = fields.Text("Mô tả")
    
    # File đính kèm
    file_tai_lieu = fields.Binary("File tài liệu", required=True)
    file_tai_lieu_name = fields.Char("Tên file")
    
    # Người upload
    nguoi_tao_id = fields.Many2one('nhan_vien', string="Người tạo")
    
    trang_thai = fields.Selection([
        ('hieu_luc', 'Đang hiệu lực'),
        ('het_han', 'Hết hạn'),
        ('thu_hoi', 'Đã thu hồi'),
    ], string="Trạng thái", default='hieu_luc')
    
    _sql_constraints = [
        ('ma_tai_lieu_unique', 'unique(ma_tai_lieu)', 'Mã tài liệu phải là duy nhất!')
    ]
