# -*- coding: utf-8 -*-
{
    'name': "Stock Extend",

    'summary': """
        Stock Extend""",

    'description': """
        Stock Extend
    """,

    'author': "Asiamatrix",
    'website': "http://www.asiamatrixsoftware.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.6',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'reports/report_stock_traceability.xml',
        'views/stock_picking_views.xml',
        'views/stock_scrap_views.xml',
    ],
}