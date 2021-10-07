# -*- coding: utf-8 -*-
{
    'name': "Customer Credit Limit",

    'summary': """Credit Limit""",

    'description': """
        Added Customer Credit Limit.
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Contact',

    'version': '1.3',

    'depends': [
        'base',
        'sale',
        'sale_management',
        'account',
        'product'
    ],

    'data': [
        'security/allow_credit_limit_security.xml',
        'views/res_partner_views.xml',
        'views/sale_views.xml',
    ],

    'installable': True,

    'application': False,
}