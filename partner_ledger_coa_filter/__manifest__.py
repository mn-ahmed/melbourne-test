# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': 'Filter Chart of Account in Partner Ledger Report',
    'version': '1.1',
    'summary': 'Filter Chart of Account in Partner Ledger Report',
    'description': """
Filter Chart of Account in Partner Ledger Report
    """,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'depends': [
        'account_reports',
        'multi_branches_reports_ent',
    ],
    'data': [
        'views/account_financial_report_asset.xml',
        'views/search_template_view.xml',
        'views/report_financial.xml'
        ],
    'demo': [],
    'images': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}