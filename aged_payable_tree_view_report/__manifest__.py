# -*- coding: utf-8 -*-
{
    'name': "Aged Payable Report",

    'summary': """Aged Payable Report""",

    'description': """
        Added aged payable tree view report in purchase report.
    """,

    'author': "THA",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Report',

    'version': '0.4',

    'depends': [
        'purchase'
    ],

    'data': [
        'security/ir.model.access.csv',
        'report/aged_payable_report_view.xml',
    ],

    'installable': True,

    'application': False,
}