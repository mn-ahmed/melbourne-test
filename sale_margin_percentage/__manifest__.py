# -*- coding: utf-8 -*-
{
    'name': "Sale Margin Percentage",

    'summary': """Added Sale Margin Percentage""",

    'description': """
        Added Sale Margin Percentage in Sale Report.
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Sale',

    'version': '13.0.1.6',

    'depends': [
        'sale',
        'sale_margin',
    ],

    'data': [
        'data/sale_margin_percentage_data.xml',
        'views/sale_views.xml',
    ],

    'images': ['static/description/icon.png'],

    'installable': True,

    'application': False,
}