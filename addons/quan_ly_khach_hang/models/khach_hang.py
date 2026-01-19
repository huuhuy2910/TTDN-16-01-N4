# -*- coding: utf-8 -*-

from odoo import models, fields, api

class KhachHang(models.Model):
    _name = 'khach_hang'
    _description = 'Quản lý thông tin khách hàng'
    _rec_name = 'ten_khach_hang'
    _order = 'ten_khach_hang asc'

    # Thông tin cơ bản
    ma_khach_hang = fields.Char("Mã khách hàng", required=True, copy=False)
    ten_khach_hang = fields.Char("Tên khách hàng", required=True)
    loai_khach_hang = fields.Selection([
        ('ca_nhan', 'Cá nhân'),
        ('doanh_nghiep', 'Doanh nghiệp'),
    ], string="Loại khách hàng", default='ca_nhan', required=True)
    
    # Thông tin liên hệ
    dia_chi = fields.Text("Địa chỉ")
    dien_thoai = fields.Char("Điện thoại")
    email = fields.Char("Email")
    website = fields.Char("Website")
    
    # Thông tin doanh nghiệp (nếu là doanh nghiệp)
    ma_so_thue = fields.Char("Mã số thuế")
    nguoi_dai_dien = fields.Char("Người đại diện")
    chuc_vu_dai_dien = fields.Char("Chức vụ người đại diện")
    
    # Thông tin cá nhân (nếu là cá nhân)
    so_cmnd_cccd = fields.Char("Số CMND/CCCD")
    ngay_sinh = fields.Date("Ngày sinh")
    gioi_tinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khac', 'Khác'),
    ], string="Giới tính")
    
    # Nhân viên phụ trách (liên kết với nhan_su)
    nhan_vien_phu_trach_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách")
    
    # Quan hệ với hồ sơ số hóa
    hop_dong_ids = fields.One2many('hop_dong', 'khach_hang_id', string="Hợp đồng")
    bao_gia_ids = fields.One2many('bao_gia', 'khach_hang_id', string="Báo giá")
    tai_lieu_ids = fields.One2many('tai_lieu', 'khach_hang_id', string="Tài liệu")
    
    # Đếm số lượng
    hop_dong_count = fields.Integer(compute="_compute_counts", string="Số hợp đồng")
    bao_gia_count = fields.Integer(compute="_compute_counts", string="Số báo giá")
    tai_lieu_count = fields.Integer(compute="_compute_counts", string="Số tài liệu")
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('moi', 'Mới'),
        ('tiem_nang', 'Tiềm năng'),
        ('dang_hop_tac', 'Đang hợp tác'),
        ('tam_dung', 'Tạm dừng'),
        ('ngung_hop_tac', 'Ngừng hợp tác'),
    ], string="Trạng thái", default='moi')
    
    ghi_chu = fields.Text("Ghi chú")
    anh = fields.Binary("Ảnh/Logo")
    
    @api.depends('hop_dong_ids', 'bao_gia_ids', 'tai_lieu_ids')
    def _compute_counts(self):
        for record in self:
            record.hop_dong_count = len(record.hop_dong_ids)
            record.bao_gia_count = len(record.bao_gia_ids)
            record.tai_lieu_count = len(record.tai_lieu_ids)
    
    def action_view_hop_dong(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp đồng',
            'res_model': 'hop_dong',
            'view_mode': 'tree,form',
            'domain': [('khach_hang_id', '=', self.id)],
            'context': {'default_khach_hang_id': self.id}
        }
    
    def action_view_bao_gia(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo giá',
            'res_model': 'bao_gia',
            'view_mode': 'tree,form',
            'domain': [('khach_hang_id', '=', self.id)],
            'context': {'default_khach_hang_id': self.id}
        }
    
    def action_view_tai_lieu(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tài liệu',
            'res_model': 'tai_lieu',
            'view_mode': 'tree,form',
            'domain': [('khach_hang_id', '=', self.id)],
            'context': {'default_khach_hang_id': self.id}
        }
    
    _sql_constraints = [
        ('ma_khach_hang_unique', 'unique(ma_khach_hang)', 'Mã khách hàng phải là duy nhất!')
    ]
