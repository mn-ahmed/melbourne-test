# -*- coding: utf-8 -*-
{
    'name': 'HR Expenses Extend',

    'version': '0.5',

    'summary': 'HR Expenses Extend',

    'description': """
       * Added base currency rate field.
    """,

    'category': 'Expense',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'hr_expense',
        'multi_branches',
    ],

    'data': [
        'data/ir_sequences.xml',
        'views/hr_expense_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
