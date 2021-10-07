# -*- coding: utf-8 -*-
{
    'name': 'Multi Scrap',

    'version': '0.2',

    'summary': 'Multi Scrap Form',

    'description': """
       * Added menu multi scrap in inventory module. 
    """,

    'category': 'Stock',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'stock',
        'account',
        'multi_branches',
    ],

    'data': [
        'data/stock_multi_scrap.xml',
        'security/ir.model.access.csv',
        'views/scrap_views.xml',
        'views/stock_view.xml',
        'views/account_move_view.xml',
        'wizard/stock_warn_insufficient_qty_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
