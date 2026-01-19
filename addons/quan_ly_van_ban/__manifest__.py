# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Văn Bản",

    'summary': """
        Quản lý hợp đồng, báo giá và tài liệu số hóa""",

    'description': """
        Module quản lý văn bản bao gồm:
        - Quản lý văn bản đến
        - Quản lý văn bản đi
        - Danh mục loại văn bản
        - Quản lý hợp đồng
        - Quản lý báo giá
        - Quản lý tài liệu số hóa
        - Liên kết với khách hàng và nhân sự
        - Tự động hóa tạo văn bản đến khi gửi duyệt hợp đồng
        - Đính kèm file văn bản
    """,

    'author': "FIT-DNU",
    'website': "https://ttdn1501.aiotlabdnu.xyz/web",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Document Management',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'nhan_su'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/loai_van_ban.xml',
        'views/van_ban_den.xml',
        'views/van_ban_di.xml',
        'views/hop_dong.xml',
        'views/bao_gia.xml',
        'views/tai_lieu.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
