# -*- coding: utf-8 -*-
{
    'name': "Purchase Item List Report",

    'summary': """Purchase Item List Report""",

    'description': """
        Added purchase item list in purchase report.
    """,

    'author': "THA",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Report',

    'version': '0.3',

    'depends': [
        'purchase','multi_branches'
    ],

    'data': [
        'security/ir.model.access.csv',
        'report/purchase_item_list_report_view.xml',
        # 'wizard/purchase_item_list_report_wizard_view.xml'
    ],

    'installable': True,

    'application': False,
}