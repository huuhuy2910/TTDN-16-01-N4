from odoo import models, fields

class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    cham_cong_ids = fields.One2many('cham_cong', 'nhan_vien_id', string='Chấm công')
    so_ngay_cham_cong = fields.Integer(string='Số ngày chấm công', compute='_compute_so_ngay_cham_cong')

    def _compute_so_ngay_cham_cong(self):
        for record in self:
            record.so_ngay_cham_cong = len(record.cham_cong_ids)

    def action_view_cham_cong(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chấm công',
            'res_model': 'cham_cong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id}
        }
