# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Global Discount And Taxes",
    'summary': """ Global Discount And Taxes""",
    'description': """
Global Discount And Taxes On
- Sale
- Purchase
- Invoice
""",
    "version": "3.25",
    "category": "Accounting/Accounting",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'stock_account',
        'sale_stock',
        'purchase_stock',
        'account',
    ],
    "data": [
        'views/config_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/account_move_view.xml',
    ],
    "application": False,
    'installable': True,
}
