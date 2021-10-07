# -*- coding: utf-8 -*-
{
    'name': 'Net Sale Report',
    'version': '0.3',
    'summary': 'Net Sale Report',
    'category': 'Sale Report',
    'website': "www.asiamatrixsoftware.com",
    'email': 'info@asiamatrixsoftware.com',
    'depends': ['sale', 'account', 'multi_branches', 'product_brand'],
    'data': [
        'security/ir.model.access.csv',
        'reports/net_sale_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
