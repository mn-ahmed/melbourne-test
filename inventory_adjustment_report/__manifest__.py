# -*- coding: utf-8 -*-
{
    'name': 'Inventory Adjustment Report',

    'version': '12.0.1.0',

    'summary': 'Stock inventory adjustment report',

    'description': """
       * Added column Cost Price and Amount in inventory adjustment report.
    """,

    'category': 'Stock',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'stock',
    ],

    'data': [
        'report/report_stockinventory.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
