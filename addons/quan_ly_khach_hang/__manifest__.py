# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Khách Hàng",
    'summary': "Quản lý thông tin khách hàng, hợp đồng, báo giá và hồ sơ số hóa",
    'description': """
        Module quản lý khách hàng bao gồm:
        - Quản lý thông tin khách hàng (cá nhân/doanh nghiệp)
        - Quản lý hợp đồng
        - Quản lý báo giá
        - Số hóa tài liệu pháp lý
        - Tích hợp với nhân sự (nhân viên phụ trách)
        - Tích hợp với văn bản (văn bản liên quan đến khách hàng)
    """,
    'author': "FIT-DNU",
    'website': "https://ttdn1501.aiotlabdnu.xyz/web",
    'category': 'Sales/CRM',
    'version': '1.0',
    'depends': ['base', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/khach_hang.xml',
        'views/hop_dong.xml',
        'views/bao_gia.xml',
        'views/van_ban_khach_hang_menu.xml',
        'views/tai_lieu.xml',
        'views/nhan_vien_extend.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
