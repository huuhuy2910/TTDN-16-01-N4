{
    'name': 'Quản Lý Công Việc',
    'version': '1.0',
    'category': 'Project Management',
    'summary': 'Quản lý công việc, giao việc và theo dõi tiến độ',
    'description': '''
        Module quản lý công việc bao gồm:
        - Giao việc cho nhân viên
        - Theo dõi tiến độ công việc
        - Quản lý dự án
        - Liên kết với nhân sự
    ''',
    'author': 'Your Name',
    'depends': ['nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/cong_viec.xml',
        'views/du_an.xml',
        'views/nhan_vien_extend.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
