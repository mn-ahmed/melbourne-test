# -*- coding: utf-8 -*-
{
    'name': "Multi Currency Landed Costs",

    'summary': """Multi Currency Landed Costs""",

    'description': """
       Multi Currency Landed Costs
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Inventory',

    'version': '0.5',

    'depends': [
        'stock_landed_costs',
        'multi_branches',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/multi_stock_landed_cost_security.xml',
        'data/multi_landed_cost_data.xml',
        'views/product_views.xml',
        'views/account_move_views.xml',
        'views/multi_stock_landed_cost_views.xml',
        'views/stock_valuation_layer_views.xml',
    ],

    'installable': True,

    'application': False,
}