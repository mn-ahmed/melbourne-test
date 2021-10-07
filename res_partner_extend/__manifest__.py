# -*- coding: utf-8 -*-
{
    'name': "Category For Partner",

    'summary': """groupby for mny2many fields in partner""",

    'description': """
        groupby for mny2many fields in partner
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Contact',

    'version': '0.1',

    'depends': [
        'base',

    ],

    'data': [

        'views/res_partner_view.xml',

    ],

    'installable': True,

    'application': False,
}