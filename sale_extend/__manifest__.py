# -*- coding: utf-8 -*-
{
    'name': "Sale Order Extend",

    'summary': """To show last sale price in sale order form""",

    'description': """
        To show last sale price in sale order form
    """,

    'author': "Asia Matrix Software Solution",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Sale',

    'version': '1.7',

    'depends': [
        'sale_enterprise',
        'hr',
        'sample_give_form',
        'base_customer_supplier',
        'product',
        'stock',
    ],

    'data': [
        'reports/sale_issues_report.xml',
        'reports/stock_sale_reports.xml',
        'reports/sale_issue_report_template.xml',
        'reports/sale_report_template_extend.xml',
        'reports/stock_sale_delivery_report_template.xml',
        'reports/stock_sale_return_report_template.xml',
        'reports/sale_report_analysis_view.xml',
        'views/account_move_views.xml',
        'views/sale_extend_views.xml',
        'views/stock_views.xml',
        'views/product_view.xml',
    ],

    'installable': True,

    'application': False,
}