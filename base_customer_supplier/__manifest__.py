# -*- coding: utf-8 -*-
{
    'name': 'Base Customer and Supplier',

    'version': '1.2',

    'summary': 'Added Customer and Supplier boolean field',

    'description': """
       * Added Customer and Supplier boolean field in contact form.
    """,

    'category': 'Contact',

    'Author': 'Asia Matrix Software Solution',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
    ],

    'data': [
        'views/partner_views.xml',
        'views/customer_views.xml',
        'views/supplier_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
