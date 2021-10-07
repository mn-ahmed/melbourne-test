# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    "name": "Inventory Adjustment BackDate",
    "summary": "Inventory Adjustment BackDate",
    "description": "Inventory Adjustment BackDate",
    "version": "1.4",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "category": "Warehouse Management",
    "depends": [
        "stock_account",
        "sale",
        "purchase",
    ],
    "data": [
        "views/user_view.xml",
        "views/stock_account_views.xml",
    ],
    'installable': True,
    'application': True,
}
