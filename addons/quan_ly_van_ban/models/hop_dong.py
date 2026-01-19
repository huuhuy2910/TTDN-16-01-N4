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
        """Chuyển trạng thái từ Nháp sang Chờ duyệt và tự động tạo văn bản đến"""
        for record in self:
            if record.trang_thai == 'nhap':
                record.trang_thai = 'cho_duyet'
                # Tự động tạo văn bản đến
                record._create_van_ban_den()
    
    def _create_van_ban_den(self):
        """Tạo văn bản đến tự động khi gửi duyệt hợp đồng"""
        self.ensure_one()
        
        # Kiểm tra xem đã có văn bản đến cho hợp đồng này chưa
        existing_vb = self.env['van_ban_den'].search([
            ('hop_dong_id', '=', self.id)
        ], limit=1)
        
        if existing_vb:
            return existing_vb
        
        # Lấy loại văn bản "Hợp đồng" hoặc tạo mới nếu chưa có
        loai_vb = self.env['loai_van_ban'].search([('ma_loai', '=', 'HD')], limit=1)
        if not loai_vb:
            loai_vb = self.env['loai_van_ban'].create({
                'ma_loai': 'HD',
                'ten_loai': 'Hợp đồng',
                'mo_ta': 'Văn bản hợp đồng',
                'hoat_dong': True
            })
        
        # Tạo số ký hiệu tự động
        count = self.env['van_ban_den'].search_count([
            ('loai_van_ban_id', '=', loai_vb.id),
            ('ngay_den', '>=', fields.Date.today().replace(month=1, day=1))
        ]) + 1
        so_ky_hieu = f"HD/{count:04d}/{fields.Date.today().year}"
        
        # Xác định người xử lý (ưu tiên nhân viên phụ trách hợp đồng)
        nguoi_xu_ly = self.nhan_vien_phu_trach_id if self.nhan_vien_phu_trach_id else False
        
        # Tạo văn bản đến
        van_ban_den = self.env['van_ban_den'].create({
            'so_ky_hieu': so_ky_hieu,
            'ngay_den': fields.Date.today(),
            'ngay_van_ban': self.ngay_ky or fields.Date.today(),
            'noi_ban_hanh': self.khach_hang_id.ten_khach_hang if self.khach_hang_id else 'Khách hàng',
            'nguoi_ky': '',
            'trich_yeu': 'Hợp đồng: {} - Khách hàng: {}'.format(self.ten_hop_dong, self.khach_hang_id.ten_khach_hang if self.khach_hang_id else ""),
            'loai_van_ban_id': loai_vb.id,
            'do_khan': 'thuong',
            'do_mat': 'binh_thuong',
            'nguoi_xu_ly_id': nguoi_xu_ly.id if nguoi_xu_ly else False,
            'trang_thai': 'moi',
            'hop_dong_id': self.id,
            'file_dinh_kem': self.file_hop_dong,
            'ten_file': self.file_hop_dong_name,
            'ghi_chu': 'Văn bản được tạo tự động khi gửi duyệt hợp đồng {}'.format(self.ma_hop_dong)
        })
        
        return van_ban_den
    
    def _create_van_ban_di(self):
        """Tạo văn bản đi tự động khi duyệt hợp đồng"""
        self.ensure_one()
        
        # Kiểm tra xem đã có văn bản đi cho hợp đồng này chưa
        existing_vb = self.env['van_ban_di'].search([
            ('hop_dong_id', '=', self.id)
        ], limit=1)
        
        if existing_vb:
            return existing_vb
        
        # Lấy loại văn bản "Hợp đồng" hoặc tạo mới nếu chưa có
        loai_vb = self.env['loai_van_ban'].search([('ma_loai', '=', 'HD')], limit=1)
        if not loai_vb:
            loai_vb = self.env['loai_van_ban'].create({
                'ma_loai': 'HD',
                'ten_loai': 'Hợp đồng',
                'mo_ta': 'Văn bản hợp đồng',
                'hoat_dong': True
            })
        
        # Tạo số ký hiệu tự động
        count = self.env['van_ban_di'].search_count([
            ('loai_van_ban_id', '=', loai_vb.id),
            ('ngay_van_ban', '>=', fields.Date.today().replace(month=1, day=1))
        ]) + 1
        so_ky_hieu = f"HD/{count:04d}/{fields.Date.today().year}"
        
        # Xác định người soạn thảo (nhân viên phụ trách hợp đồng)
        nguoi_soan_thao = self.nhan_vien_phu_trach_id if self.nhan_vien_phu_trach_id else False
        
        # Xác định đơn vị soạn thảo từ nhân viên
        don_vi_soan_thao = False  # Temporarily set to False since nhan_vien may not have don_vi_id
        
        # Xác định người ký (người duyệt - có thể là người dùng hiện tại)
        nguoi_ky = self.env.user.name
        
        # Tạo văn bản đi
        van_ban_di = self.env['van_ban_di'].create({
            'so_ky_hieu': so_ky_hieu,
            'ngay_van_ban': fields.Date.today(),
            'ngay_gui': fields.Date.today(),
            'noi_nhan': self.khach_hang_id.ten_khach_hang if self.khach_hang_id else 'Khách hàng',
            'nguoi_ky': nguoi_ky,
            'trich_yeu': 'Duyệt hợp đồng: {} - Khách hàng: {}'.format(self.ten_hop_dong, self.khach_hang_id.ten_khach_hang if self.khach_hang_id else ""),
            'loai_van_ban_id': loai_vb.id,
            'do_khan': 'thuong',
            'do_mat': 'binh_thuong',
            'nguoi_soan_thao_id': nguoi_soan_thao.id if nguoi_soan_thao else False,
            'don_vi_soan_thao_id': don_vi_soan_thao.id if don_vi_soan_thao else False,
            'trang_thai': 'da_gui',  # Đã duyệt và gửi
            'hop_dong_id': self.id,
            'file_dinh_kem': self.file_hop_dong,
            'ten_file': self.file_hop_dong_name,
            'ghi_chu': 'Văn bản được tạo tự động khi duyệt hợp đồng {}'.format(self.ma_hop_dong)
        })
        
        return van_ban_di
    
    def action_approve(self):
        """Duyệt hợp đồng - chuyển sang Hiệu lực và tự động tạo văn bản đi"""
        for record in self:
            if record.trang_thai == 'cho_duyet':
                record.trang_thai = 'hieu_luc'
                # Tự động tạo văn bản đi
                record._create_van_ban_di()
                # Cập nhật trạng thái văn bản đến thành đã xử lý
                van_ban_den = self.env['van_ban_den'].search([('hop_dong_id', '=', record.id)], limit=1)
                if van_ban_den:
                    van_ban_den.write({'trang_thai': 'da_xu_ly'})
    
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