# -*- coding: utf-8 -*-
from odoo import models, fields, api

class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Quản lý văn bản đi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'so_ky_hieu'
    _order = 'ngay_van_ban desc'
    
    # Thông tin cơ bản
    so_ky_hieu = fields.Char("Số/Ký hiệu", required=True, copy=False)
    ngay_van_ban = fields.Date("Ngày văn bản", required=True, default=fields.Date.today)
    ngay_gui = fields.Date("Ngày gửi")
    noi_nhan = fields.Char("Nơi nhận", required=True)
    nguoi_ky = fields.Char("Người ký", required=True)
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
    
    # Soạn thảo
    nguoi_soan_thao_id = fields.Many2one('nhan_vien', string="Người soạn thảo", ondelete='set null')
    don_vi_soan_thao_id = fields.Many2one('don_vi', string="Đơn vị soạn thảo", ondelete='set null')
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('du_thao', 'Dự thảo'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_gui', 'Đã gửi'),
        ('huy', 'Hủy')
    ], string="Trạng thái", default='du_thao', tracking=True)
    
    # File đính kèm
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file = fields.Char("Tên file")
    
    # Ghi chú
    ghi_chu = fields.Text("Ghi chú")
    
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
                ('ngay_van_ban', '>=', fields.Date.today().replace(month=1, day=1))
            ]) + 1
            self.so_ky_hieu = f"{self.loai_van_ban_id.ma_loai}/{count:04d}/{fields.Date.today().year}"
    
    def action_gui_duyet(self):
        """Gửi văn bản đi duyệt"""
        self.write({'trang_thai': 'cho_duyet'})
    
    def action_duyet(self):
        """Duyệt văn bản đi"""
        self.write({'trang_thai': 'da_duyet'})
    
    def action_gui_van_ban(self):
        """Đánh dấu văn bản đã được gửi"""
        self.write({
            'trang_thai': 'da_gui',
            'ngay_gui': fields.Date.today()
        })

