from odoo import models, fields, api

class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Công việc'
    _order = 'ngay_bat_dau desc'

    name = fields.Char(string='Tên công việc', required=True)
    mo_ta = fields.Text(string='Mô tả')
    nhan_vien_id = fields.Many2one('nhan_vien', string='Người thực hiện', required=True)
    nguoi_giao_id = fields.Many2one('nhan_vien', string='Người giao việc')
    du_an_id = fields.Many2one('du_an', string='Dự án')
    
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu', required=True, default=fields.Date.today)
    ngay_ket_thuc = fields.Date(string='Ngày kết thúc')
    deadline = fields.Date(string='Deadline')
    
    trang_thai = fields.Selection([
        ('moi', 'Mới'),
        ('dang_thuc_hien', 'Đang thực hiện'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tam_dung', 'Tạm dừng'),
        ('huy', 'Hủy')
    ], string='Trạng thái', default='moi', required=True)
    
    muc_do_uu_tien = fields.Selection([
        ('thap', 'Thấp'),
        ('trung_binh', 'Trung bình'),
        ('cao', 'Cao'),
        ('khan_cap', 'Khẩn cấp')
    ], string='Mức độ ưu tiên', default='trung_binh')
    
    tien_do = fields.Integer(string='Tiến độ (%)', default=0)
    ghi_chu = fields.Text(string='Ghi chú')
    
    @api.onchange('trang_thai')
    def _onchange_trang_thai(self):
        if self.trang_thai == 'hoan_thanh':
            self.tien_do = 100
            if not self.ngay_ket_thuc:
                self.ngay_ket_thuc = fields.Date.today()
