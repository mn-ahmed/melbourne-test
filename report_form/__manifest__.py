# -*- coding: utf-8 -*-
{
    'name': "All Report Templates",
    'summary': """
        All report templates""",
    'description': """
        Templates for Sales,Purchase,Invoice and Inventory
    """,
    'author': "znl",
    'website': "http://www.asiamatrixsoftware.com",
    'category': 'Report',
    'version': '0.4',
    'depends': ['web','purchase','stock','account','sale','sale_extend'],
    'data': [
        'views/report.xml',
        'views/invoice_report.xml',
        'views/mandalay_invoice_report.xml',
        'views/yangon_invoice_report.xml',
        'views/sale_report.xml',
        'views/mandalay_sale_report.xml',
        'views/yangon_sale_report.xml',
        'views/purchase_order_report.xml',
        'views/purchase_quotaion_report.xml',
    ],
}