# -*- coding: utf-8 -*-
{
    'name': "Quản lý văn bản",

    'summary': """
        Module quản lý văn bản đến và văn bản đi""",

    'description': """
        Module quản lý văn bản bao gồm:
        - Loại văn bản
        - Văn bản đến
        - Văn bản đi
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Document Management',
    'version': '0.1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'views/loai_van_ban.xml',
        'views/van_ban_den.xml',
        'views/van_ban_di.xml',
        'views/menu.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,  # Đảm bảo có thể cài
    'application': True,  # Quan trọng: để hiển thị trong Apps như một ứng dụng
    'auto_install': False,
}
