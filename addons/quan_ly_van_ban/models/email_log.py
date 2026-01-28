# -*- coding: utf-8 -*-

from odoo import models, fields


class EmailLog(models.Model):
    _name = 'qlvb.email.log'
    _description = 'Nhật ký gửi email tự động'
    _order = 'sent_date desc, id desc'

    name = fields.Char("Tên log", required=True)
    model_name = fields.Char("Model")
    res_id = fields.Integer("ID bản ghi")
    res_name = fields.Char("Tên bản ghi")
    email_to = fields.Char("Email nhận")
    email_from = fields.Char("Email gửi")
    subject = fields.Char("Tiêu đề")
    status = fields.Selection([
        ('sent', 'Đã gửi'),
        ('failed', 'Thất bại'),
    ], string="Trạng thái", default='sent')
    error_message = fields.Text("Lỗi")
    mail_id = fields.Many2one('mail.mail', string="Mail")
    template_xmlid = fields.Char("Template XMLID")
    sent_date = fields.Datetime("Thời gian gửi", default=fields.Datetime.now)
