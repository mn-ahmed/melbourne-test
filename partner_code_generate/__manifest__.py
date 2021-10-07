# -*- coding: utf-8 -*-
{
    'name': "Customer Code Generation",

    'summary': """Added Customer Code Generation""",

    'description': """
        Added Customer Code Generation.
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Contact',

    'version': '0.3',

    'depends': [
        'base',
        'base_customer_supplier',
    ],

    'data': [
        'data/sequence.xml',
        'views/res_partner_views.xml',
        'views/res_country_view.xml',
        'wizard/partner_sequence.xml',

    ],

    'installable': True,

    'application': False,
}