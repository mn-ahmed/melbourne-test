# -*- coding: utf-8 -*-
{
    'name': 'Hide Price',
    'version': '0.1',
    'summary': 'Hide Price in Views, Reports.',
    'category': 'Inventory',
    'Author': 'Asia Matrix Software Solution',
    'website': "www.asiamatrixsoftware.com",
    'email': 'info@asiamatrixsoftware.com',
    'depends': [
        'consignment_management',
    ],
    'data': [
        'security/res_groups.xml',
        'views/product_views.xml',
        'views/inventory_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
