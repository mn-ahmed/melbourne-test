# -*- coding: utf-8 -*-
{
    'name': "Customer Credit Limit Report",

    'summary': """Customer Credit Limit Report""",

    'description': """
        Added customer credit limit report in account report.
    """,

    'author': "THA",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Report',

    'version': '0.3',

    'depends': [
        'customer_credit_limit',
        'account_reports'
    ],

    'data': [
        'security/ir.model.access.csv',
        'report/customer_credit_limit_report_view.xml',
        # 'wizard/customer_credit_limit_report_wizard_view.xml'
    ],

    'installable': True,

    'application': False,
}