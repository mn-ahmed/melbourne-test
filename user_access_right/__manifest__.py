# -*- coding: utf-8 -*-
{
    'name': "User Access Right",

    'summary': """Access Right Module""",

    'description': """
        This Module Add user access right.
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Security',

    'version': '0.1',

    'depends': [
        'stock',
        'sale',
        'purchase',
        'account',
        'point_of_sale',
        'multi_branches',
    ],

    'data': [
        'security/sale_access_views.xml',
        'security/purchase_access_views.xml',
        'security/account_access_views.xml',
        'security/inventory_access_views.xml',
        'security/pos_access_views.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/stock_views.xml',
        'views/point_of_sale_views.xml',
        'views/account_views.xml','views/product_cost_view.xml',
    ],

    'images': ['static/description/icon.png'],
}