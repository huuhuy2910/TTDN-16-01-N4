# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VanBanDiSignatureWizard(models.TransientModel):
    _name = 'van.ban.di.signature.wizard'
    _description = 'Upload chữ ký văn bản đi'

    van_ban_di_id = fields.Many2one('van_ban_di', string='Văn bản đi', required=True, ondelete='cascade')
    chu_ky_anh = fields.Binary('File chữ ký', required=True)
    ten_chu_ky_anh = fields.Char('Tên file chữ ký')
    preview_image = fields.Binary('Xem trước', compute='_compute_preview_image', readonly=True)

    @api.depends('chu_ky_anh', 'ten_chu_ky_anh')
    def _compute_preview_image(self):
        for wizard in self:
            filename = (wizard.ten_chu_ky_anh or '').lower()
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                wizard.preview_image = wizard.chu_ky_anh
            else:
                wizard.preview_image = False

    def action_confirm(self):
        self.ensure_one()
        if not self.chu_ky_anh:
            return {'type': 'ir.actions.act_window_close'}
        self.van_ban_di_id.write({
            'chu_ky_anh': self.chu_ky_anh,
            'ten_chu_ky_anh': self.ten_chu_ky_anh,
        })
        self.van_ban_di_id.action_ky_van_ban()
        return {'type': 'ir.actions.act_window_close'}
