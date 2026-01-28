# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class HopDongSignatureWizard(models.TransientModel):
    _name = 'hop_dong.signature.wizard'
    _description = 'Upload chữ ký hợp đồng'

    hop_dong_id = fields.Many2one('hop_dong', string='Hợp đồng', required=True)
    chu_ky_hinh_anh = fields.Binary(string='Ảnh chữ ký', required=True)
    chu_ky_hinh_anh_name = fields.Char(string='Tên file chữ ký')
    preview_image = fields.Binary(string='Xem trước', compute='_compute_preview', store=False)

    @api.depends('chu_ky_hinh_anh')
    def _compute_preview(self):
        for record in self:
            record.preview_image = record.chu_ky_hinh_anh

    def action_confirm(self):
        self.ensure_one()
        if not self.chu_ky_hinh_anh:
            raise UserError("Vui lòng tải ảnh chữ ký trước khi xác nhận.")
        values = {
            'chu_ky_hinh_anh': self.chu_ky_hinh_anh,
            'chu_ky_hinh_anh_name': self.chu_ky_hinh_anh_name,
        }
        if not self.hop_dong_id.ngay_ky_xac_nhan:
            values['ngay_ky_xac_nhan'] = fields.Datetime.now()
        self.hop_dong_id.write(values)
        return {'type': 'ir.actions.act_window_close'}
