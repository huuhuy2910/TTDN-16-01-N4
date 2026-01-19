# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NhanVienExtendKhachHang(models.Model):
    _inherit = 'nhan_vien'
    
    # Khách hàng phụ trách
    khach_hang_phu_trach_ids = fields.One2many(
        'khach_hang', 
        'nhan_vien_phu_trach_id', 
        string="Khách hàng phụ trách")
    
    hop_dong_phu_trach_ids = fields.One2many(
        'hop_dong',
        'nhan_vien_phu_trach_id',
        string="Hợp đồng phụ trách")
    
    bao_gia_lap_ids = fields.One2many(
        'bao_gia',
        'nhan_vien_lap_id',
        string="Báo giá đã lập")
    
    # Đếm số lượng
    khach_hang_count = fields.Integer(compute="_compute_khach_hang_count", string="Số khách hàng")
    hop_dong_phu_trach_count = fields.Integer(compute="_compute_khach_hang_count", string="Số hợp đồng")
    
    @api.depends('khach_hang_phu_trach_ids', 'hop_dong_phu_trach_ids')
    def _compute_khach_hang_count(self):
        for record in self:
            record.khach_hang_count = len(record.khach_hang_phu_trach_ids)
            record.hop_dong_phu_trach_count = len(record.hop_dong_phu_trach_ids)
    
    def action_view_khach_hang(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Khách hàng phụ trách',
            'res_model': 'khach_hang',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_phu_trach_id', '=', self.id)],
            'context': {'default_nhan_vien_phu_trach_id': self.id}
        }
    
    def action_view_hop_dong_phu_trach(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp đồng phụ trách',
            'res_model': 'hop_dong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_phu_trach_id', '=', self.id)],
            'context': {'default_nhan_vien_phu_trach_id': self.id}
        }
