from odoo import models, fields

class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    cong_viec_ids = fields.One2many('cong_viec', 'nhan_vien_id', string='Công việc')
    so_cong_viec = fields.Integer(string='Số công việc', compute='_compute_so_cong_viec')

    def _compute_so_cong_viec(self):
        for record in self:
            record.so_cong_viec = len(record.cong_viec_ids)

    def action_view_cong_viec(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công việc',
            'res_model': 'cong_viec',
            'view_mode': 'tree,form,kanban',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id}
        }
