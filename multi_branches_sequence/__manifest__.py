# -*- coding: utf-8 -*-
{
    'name': "Multi Branch Sequence",

    'summary': """Multi Branch Sequence""",

    'description': """
        Sale, Purchase, 
        Customer Invoice, Vendor Bill,
        Credit Note, Refund and Payment 
        added multi branch sequence number.
    """,

    'author': "asiamatrix",

    'website': "http://www.asiamatrixsoftware.com",

    'category': 'Accounting',

    'version': '0.1',

    'depends': [
        'account',
        'sale',
        'purchase',
        'multi_branches',
    ],

    'data': [
        'views/branches_sequence.xml',
    ],
}