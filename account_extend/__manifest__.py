# -*- coding: utf-8 -*-
{
    'name': "Accounting Extend",

    'summary': """
        Add Total Payment Amount in invoice list view""",

    'description': """
        Add Total Payment Amount in invoice list view
    """,

    'author': "znl",
    'website': "http://www.asiamatrixsoftware.com",
    'category': 'Accounting',
    'version': '0.9',
    'depends': ['account'],
    'data': [
        'report/account_invoice_report_view.xml',
        'views/account_move_view.xml',

    ],
}