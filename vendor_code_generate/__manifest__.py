# -*- coding: utf-8 -*-
{
    'name': "Vendor Code Generation",

    'summary': """Added Vendor Code Generation""",

    'description': """
        Added Vendor Code Generation.
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Contact',

    'version': '0.2',

    'depends': [
        'base',
        'base_customer_supplier',
    ],

    'data': [
        'data/sequence.xml',
        'views/res_partner_view.xml',


    ],

    'installable': True,

    'application': False,
}