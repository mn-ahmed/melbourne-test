# -*- coding: utf-8 -*-
{
    'name': "Stock Onhand Internal",

    'summary': """Show internal location in product search bar""",

    'description': """
       Show internal location in product search bar
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Inventory',

    'version': '13.0.1.0',

    'depends': [
        'stock',
    ],

    'data': [
        'views/stock_quant_views.xml',
    ],

    'installable': True,

    'application': False,
}