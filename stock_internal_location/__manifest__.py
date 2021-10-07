# -*- coding: utf-8 -*-
{
    'name': "Stock Internal Location",

    'summary': """Show internal location in Location Fields""",

    'description': """
       Show internal location in Location Fields
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Inventory',

    'version': '13.0.1.0',

    'depends': [
        'stock',
    ],

    'data': [
        'views/stock_picking_views.xml',
    ],

    'installable': True,

    'application': False,
}