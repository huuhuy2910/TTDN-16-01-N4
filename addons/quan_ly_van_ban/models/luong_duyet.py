# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class LuongDuyet(models.Model):
    _name = 'luong.duyet'
    _description = 'Luồng duyệt văn bản'
    _order = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Tên luồng', required=True, tracking=True)
    ma_luong = fields.Char('Mã luồng', required=True, tracking=True)
    sequence = fields.Integer('Thứ tự', default=10)
    
    loai_van_ban = fields.Selection([
        ('hop_dong', 'Hợp đồng'),
        ('bao_gia', 'Báo giá'),
        ('van_ban_di', 'Văn bản đi'),
        ('quyet_dinh', 'Quyết định'),
    ], string='Loại văn bản', required=True)
    
    active = fields.Boolean('Hoạt động', default=True)
    mo_ta = fields.Text('Mô tả')
    
    # Điều kiện áp dụng
    dieu_kien_gia_tri_min = fields.Float('Giá trị tối thiểu')
    dieu_kien_gia_tri_max = fields.Float('Giá trị tối đa')
    
    # Các bước duyệt
    buoc_duyet_ids = fields.One2many('buoc.duyet', 'luong_duyet_id', string='Các bước duyệt')
    
    # Thời gian
    thoi_gian_xu_ly_du_kien = fields.Integer('Thời gian xử lý dự kiến (giờ)', default=24)
    
    # Statistics
    so_lan_su_dung = fields.Integer('Số lần sử dụng', compute='_compute_statistics')
    so_van_ban_dang_cho = fields.Integer('Đang chờ duyệt', compute='_compute_statistics')
    
    @api.depends('ma_luong')
    def _compute_statistics(self):
        for record in self:
            # Count in different models based on loai_van_ban
            if record.loai_van_ban == 'hop_dong':
                record.so_lan_su_dung = self.env['hop.dong'].search_count([('luong_duyet_id', '=', record.id)])
                record.so_van_ban_dang_cho = self.env['hop.dong'].search_count([
                    ('luong_duyet_id', '=', record.id),
                    ('trang_thai', '=', 'cho_duyet')
                ])
            else:
                record.so_lan_su_dung = 0
                record.so_van_ban_dang_cho = 0
    
    @api.model
    def get_luong_duyet(self, loai_van_ban, gia_tri=0):
        """Lấy luồng duyệt phù hợp dựa trên loại và giá trị"""
        domain = [
            ('loai_van_ban', '=', loai_van_ban),
            ('active', '=', True),
        ]
        
        if gia_tri > 0:
            domain.extend([
                ('dieu_kien_gia_tri_min', '<=', gia_tri),
                ('dieu_kien_gia_tri_max', '>=', gia_tri),
            ])
        
        return self.search(domain, order='sequence', limit=1)


class BuocDuyet(models.Model):
    _name = 'buoc.duyet'
    _description = 'Bước duyệt trong luồng'
    _order = 'sequence'
    
    name = fields.Char('Tên bước', required=True)
    sequence = fields.Integer('Thứ tự', required=True)
    luong_duyet_id = fields.Many2one('luong.duyet', string='Luồng duyệt', required=True, ondelete='cascade')
    
    # Người duyệt
    loai_nguoi_duyet = fields.Selection([
        ('chuc_vu', 'Theo chức vụ'),
        ('phong_ban', 'Theo phòng ban'),
        ('nguoi_cu_the', 'Người cụ thể'),
    ], string='Loại người duyệt', required=True, default='chuc_vu')
    
    chuc_vu = fields.Char('Chức vụ')
    # phong_ban_id = fields.Many2one('phong.ban', string='Phòng ban')
    nguoi_duyet_ids = fields.Many2many('nhan_vien', string='Người duyệt cụ thể')
    
    # Cấu hình duyệt
    bat_buoc = fields.Boolean('Bắt buộc', default=True)
    cho_phep_tu_choi = fields.Boolean('Cho phép từ chối', default=True)
    thoi_gian_xu_ly = fields.Integer('Thời gian xử lý (giờ)', default=24)
    
    # Hành động sau khi duyệt
    hanh_dong_sau_duyet = fields.Selection([
        ('next', 'Chuyển bước tiếp theo'),
        ('complete', 'Hoàn thành'),
        ('notify', 'Thông báo'),
    ], string='Hành động', default='next')
    
    ghi_chu = fields.Text('Ghi chú')


class LichSuDuyet(models.Model):
    _name = 'lich.su.duyet'
    _description = 'Lịch sử duyệt văn bản'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Tên', compute='_compute_name', store=True)
    
    van_ban_type = fields.Selection([
        ('hop_dong', 'Hợp đồng'),
        ('bao_gia', 'Báo giá'),
        ('van_ban_di', 'Văn bản đi'),
    ], string='Loại văn bản', required=True)
    van_ban_id = fields.Integer('ID Văn bản', required=True)
    
    luong_duyet_id = fields.Many2one('luong.duyet', string='Luồng duyệt')
    buoc_duyet_id = fields.Many2one('buoc.duyet', string='Bước duyệt')
    
    nguoi_duyet_id = fields.Many2one('nhan_vien', string='Người duyệt', required=True, tracking=True)
    ngay_duyet = fields.Datetime('Ngày duyệt', default=fields.Datetime.now, tracking=True)
    
    hanh_dong = fields.Selection([
        ('submit', 'Gửi duyệt'),
        ('approve', 'Phê duyệt'),
        ('reject', 'Từ chối'),
        ('cancel', 'Hủy'),
        ('request_change', 'Yêu cầu sửa'),
    ], string='Hành động', required=True, tracking=True)
    
    trang_thai = fields.Selection([
        ('pending', 'Chờ xử lý'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ], string='Trạng thái', default='pending', tracking=True)
    
    y_kien = fields.Text('Ý kiến', tracking=True)
    file_dinh_kem = fields.Binary('File đính kèm')
    file_name = fields.Char('Tên file')
    
    @api.depends('van_ban_type', 'hanh_dong', 'nguoi_duyet_id')
    def _compute_name(self):
        for record in self:
            record.name = f'{record.van_ban_type} - {record.hanh_dong} - {record.nguoi_duyet_id.name}'

    def action_extract_and_summarize(self):
        """Trích xuất và tóm tắt nội dung file đính kèm trong lịch sử duyệt"""
        self.ensure_one()
        
        if not self.file_dinh_kem:
            raise models.ValidationError("Không có file đính kèm để xử lý")
        
        try:
            # Gọi chatbot service để xử lý file
            result = self.env['chatbot.service'].process_uploaded_file(
                file_data=self.file_dinh_kem,
                file_name=self.file_name or 'file_attachment',
                model_key='openai_gpt4o_mini',
                question="Hãy trích xuất nội dung chính và tóm tắt văn bản này"
            )
            
            if result.get('success'):
                # Cập nhật ý kiến với nội dung tóm tắt
                summary = result.get('summary', result.get('answer', ''))
                if summary:
                    current_y_kien = self.y_kien or ''
                    new_y_kien = f"{current_y_kien}\n\n[Tóm tắt AI]: {summary}".strip()
                    self.write({
                        'y_kien': new_y_kien
                    })
                    self.message_post(body=f"Đã thêm tóm tắt từ AI:\n{summary}")
                else:
                    self.message_post(body="AI không thể tạo tóm tắt cho văn bản này")
            else:
                error_msg = result.get('error', 'Lỗi không xác định')
                self.message_post(body=f"Lỗi khi xử lý file: {error_msg}")
                
        except Exception as e:
            self.message_post(body=f"Lỗi hệ thống: {str(e)}")
            raise
