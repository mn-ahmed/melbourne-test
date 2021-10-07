# -*- coding: utf-8 -*-
{
    'name': 'Expense Signature',

    'version': '0.2',

    'summary': 'Expense Signatrue',

    'description': """
       * Added signature in expense form.
       * Click Approval show login user signature.
       * This Signature show PDF.
       * V2- added approved datetime.
    """,

    'category': 'Expense',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'hr_expense',
        'expense_extend',
    ],

    'data': [
        'views/res_user_views.xml',
        'views/hr_expense_views.xml',
        'report/hr_expense_report.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
