content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="mail_template_hop_dong_draft_reminder" model="mail.template">
            <field name="name">Nhac hoan thien hop dong (nhap)</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Nhac hoan thien hop dong</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.nhan_vien_phu_trach_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
        
        <record id="mail_template_hop_dong_submit_approval" model="mail.template">
            <field name="name">Yeu cau duyet hop dong</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Yeu cau duyet hop dong</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.nhan_vien_phu_trach_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
        
        <record id="mail_template_hop_dong_approval_reminder" model="mail.template">
            <field name="name">Nhac duyet hop dong</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Nhac duyet hop dong</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.nhan_vien_phu_trach_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
        
        <record id="mail_template_hop_dong_approved_customer" model="mail.template">
            <field name="name">Hop dong da duoc duyet</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Hop dong da duoc duyet</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.khach_hang_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
        
        <record id="mail_template_hop_dong_expiry_warning" model="mail.template">
            <field name="name">Canh bao hop dong sap het han</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Canh bao hop dong sap het han</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.khach_hang_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
        
        <record id="mail_template_hop_dong_expired_notice" model="mail.template">
            <field name="name">Thong bao hop dong da het han</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Thong bao hop dong da het han</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.khach_hang_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
        
        <record id="mail_template_hop_dong_effective_reminder" model="mail.template">
            <field name="name">Nhac lich ky truoc ngay hieu luc</field>
            <field name="model_id" ref="model_hop_dong"/>
            <field name="subject">Nhac lich ky hop dong</field>
            <field name="email_from">${(user.email_formatted or '')}</field>
            <field name="email_to">${object.khach_hang_id.email or ''}</field>
            <field name="body_html" type="html"><![CDATA[<p>Test email</p>]]></field>
        </record>
    </data>
</odoo>
'''

with open('/home/easylove04/Business-Internship/addons/quan_ly_khach_hang/data/mail_templates.xml', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('File created successfully')

# Verify
import lxml.etree as etree
schema = etree.RelaxNG(etree.parse('/home/easylove04/Business-Internship/odoo/import_xml.rng'))
doc = etree.parse('/home/easylove04/Business-Internship/addons/quan_ly_khach_hang/data/mail_templates.xml')
print('Valid:', schema.validate(doc))
if not schema.validate(doc):
    for e in schema.error_log:
        print(f"  Line {e.line}: {e.message}")
