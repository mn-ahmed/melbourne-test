# -*- coding: utf-8 -*-
{
    'name': 'Customer Form',

    'version': '0.2',

    'summary': 'Prepare Customer Form',

    'description': """
       * Prepare Customer and Sale Form.
    """,

    'category': 'Contact',

    'Author': 'Asia Matrix Software Solution',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'base',
        'sale',
        'multi_branches',
    ],

    'data': [
        'views/partner_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
