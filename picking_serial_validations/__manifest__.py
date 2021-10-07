# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Picking Serial Validations",
    'summary': """
Picking Serial Validations
""",
    'description': """
- Serial Validations:
    - Missing Serial Number
    - Serial Number not belongs from same product
    - While return/sale must have sufficient quantity
    - Same serial number return

- Validation applied on
    - Purchase
    - Purchase Return
    - Sale
    - Sale Return

    """,
    "version": "1.8",
    "category": "Operations/Inventory",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'stock'
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    "application": False,
    'installable': True,
}
