# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class GiaoHangConfirmWizard(models.TransientModel):
    _name = 'giao_hang.confirm.wizard'
    _description = 'Xác nhận giao hàng - Upload chữ ký và ảnh xác nhận'

    giao_hang_id = fields.Many2one('giao_hang', string='Giao hàng', required=True)
    nguoi_nhan = fields.Char(string='Người nhận')
    nguoi_ky_nhan = fields.Char(string='Người ký nhận')
    ngay_ky_nhan = fields.Date(string='Ngày ký nhận', default=fields.Date.today)
    chu_ky_dien_tu = fields.Binary(string='Chữ ký điện tử', required=True)
    chu_ky_dien_tu_name = fields.Char(string='Tên file chữ ký')
    anh_xac_nhan = fields.Binary(string='Ảnh xác nhận giao hàng', required=True)
    anh_xac_nhan_name = fields.Char(string='Tên file ảnh')
    preview_signature = fields.Binary(string='Xem trước chữ ký', compute='_compute_preview', store=False)
    preview_photo = fields.Binary(string='Xem trước ảnh', compute='_compute_preview', store=False)

    @api.depends('chu_ky_dien_tu', 'anh_xac_nhan')
    def _compute_preview(self):
        for record in self:
            record.preview_signature = record.chu_ky_dien_tu
            record.preview_photo = record.anh_xac_nhan

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        giao_hang_id = self.env.context.get('default_giao_hang_id')
        if giao_hang_id:
            giao_hang = self.env['giao_hang'].browse(giao_hang_id)
            if giao_hang.exists():
                res.setdefault('nguoi_nhan', giao_hang.nguoi_nhan)
                res.setdefault('nguoi_ky_nhan', giao_hang.nguoi_ky_nhan or giao_hang.nguoi_nhan)
        return res

    def action_confirm(self):
        self.ensure_one()
        if not self.chu_ky_dien_tu or not self.anh_xac_nhan:
            raise UserError("Vui lòng tải chữ ký và ảnh xác nhận giao hàng trước khi xác nhận.")
        giao_hang = self.giao_hang_id
        values = {
            'trang_thai': 'da_giao',
            'ngay_giao_hang_thuc_te': fields.Date.today(),
            'nguoi_nhan': self.nguoi_nhan,
            'nguoi_ky_nhan': self.nguoi_ky_nhan,
            'ngay_ky_nhan': self.ngay_ky_nhan or fields.Date.today(),
            'chu_ky_dien_tu': self.chu_ky_dien_tu,
            'anh_xac_nhan': self.anh_xac_nhan,
        }
        giao_hang.write(values)
        giao_hang._create_hoa_don_from_giao_hang()
        giao_hang._send_da_giao_email()
        return {'type': 'ir.actions.act_window_close'}
