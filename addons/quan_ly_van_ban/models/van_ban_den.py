# -*- coding: utf-8 -*-
from odoo import models, fields, api

class VanBanDen(models.Model):
    _name = 'van_ban_den'
    _description = 'Quản lý văn bản đến'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'so_ky_hieu'
    _order = 'ngay_den desc'
    
    # Thông tin cơ bản
    so_ky_hieu = fields.Char("Số/Ký hiệu", required=True, copy=False)
    ngay_den = fields.Date("Ngày đến", required=True, default=fields.Date.today)
    ngay_van_ban = fields.Date("Ngày văn bản", required=True)
    noi_ban_hanh = fields.Char("Nơi ban hành", required=True)
    nguoi_ky = fields.Char("Người ký")
    trich_yeu = fields.Text("Trích yếu", required=True)
    
    # Phân loại
    loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản", required=True, ondelete='restrict')
    do_khan = fields.Selection([
        ('thuong', 'Thường'),
        ('khan', 'Khẩn'),
        ('hoa_toc', 'Hỏa tốc'),
        ('thuong_khat', 'Thượng khẩn')
    ], string="Độ khẩn", default='thuong')
    do_mat = fields.Selection([
        ('binh_thuong', 'Bình thường'),
        ('mat', 'Mật'),
        ('toi_mat', 'Tối mật')
    ], string="Độ mật", default='binh_thuong')
    
    # Xử lý
    nguoi_xu_ly_id = fields.Many2one('nhan_vien', string="Người xử lý", ondelete='set null', tracking=True)
    han_xu_ly = fields.Date("Hạn xử lý", tracking=True)
    trang_thai = fields.Selection([
        ('moi', 'Mới'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
        ('chuyen_tiep', 'Chuyển tiếp')
    ], string="Trạng thái", default='moi', tracking=True)
    
    # File đính kèm
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file = fields.Char("Tên file")
    
    # Ghi chú
    ghi_chu = fields.Text("Ghi chú")
    
    lan_dau_xem = fields.Boolean(string="Đã xem lần đầu", default=False)
    
    # Liên kết với hợp đồng (nếu có)
    hop_dong_id = fields.Many2one('hop_dong', string="Hợp đồng liên quan", ondelete='set null')
    
    # Audit
    nguoi_tao_id = fields.Many2one('res.users', string="Người tạo", default=lambda self: self.env.user, readonly=True)
    ngay_tao = fields.Datetime("Ngày tạo", default=fields.Datetime.now, readonly=True)
    
    _sql_constraints = [
        ('so_ky_hieu_unique', 'unique(so_ky_hieu)', 'Số/Ký hiệu văn bản đã tồn tại!')
    ]
    
    @api.onchange('loai_van_ban_id')
    def _onchange_loai_van_ban(self):
        """Tự động gợi ý số ký hiệu dựa trên loại văn bản"""
        if self.loai_van_ban_id and not self.so_ky_hieu:
            # Đếm số văn bản cùng loại trong năm
            count = self.search_count([
                ('loai_van_ban_id', '=', self.loai_van_ban_id.id),
                ('ngay_den', '>=', fields.Date.today().replace(month=1, day=1))
            ]) + 1
            self.so_ky_hieu = f"{self.loai_van_ban_id.ma_loai}/{count:04d}/{fields.Date.today().year}"
    
    def action_mark_as_processing(self):
        for record in self:
            if not record.lan_dau_xem:
                record.write({'lan_dau_xem': True, 'trang_thai': 'dang_xu_ly'})

