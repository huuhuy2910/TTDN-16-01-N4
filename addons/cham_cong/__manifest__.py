{
    'name': 'Chấm Công',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Quản lý chấm công và thời gian làm việc',
    'description': 'Module để quản lý chấm công, theo dõi thời gian làm việc của nhân viên.',
    'author': 'Your Name',
    'depends': ['nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/cham_cong.xml',
        'views/nhan_vien_extend.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}