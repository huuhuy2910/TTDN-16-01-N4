from odoo import models, fields

class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Dự án'
    _order = 'ngay_bat_dau desc'

    name = fields.Char(string='Tên dự án', required=True)
    ma_du_an = fields.Char(string='Mã dự án', required=True)
    mo_ta = fields.Text(string='Mô tả')
    
    quan_ly_id = fields.Many2one('nhan_vien', string='Quản lý dự án', required=True)
    thanh_vien_ids = fields.Many2many('nhan_vien', string='Thành viên')
    cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string='Công việc')
    
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu', required=True)
    ngay_ket_thuc = fields.Date(string='Ngày kết thúc')
    
    trang_thai = fields.Selection([
        ('ke_hoach', 'Kế hoạch'),
        ('dang_thuc_hien', 'Đang thực hiện'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tam_dung', 'Tạm dừng'),
        ('huy', 'Hủy')
    ], string='Trạng thái', default='ke_hoach', required=True)
    
    ngan_sach = fields.Float(string='Ngân sách')
    ghi_chu = fields.Text(string='Ghi chú')
    
    so_cong_viec = fields.Integer(string='Số công việc', compute='_compute_so_cong_viec', store=True)
    
    def _compute_so_cong_viec(self):
        for record in self:
            record.so_cong_viec = len(record.cong_viec_ids)
