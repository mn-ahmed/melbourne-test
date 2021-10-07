# -*- coding: utf-8 -*-
{
    'name': "Inventory Report In-Out Excel",
    'summary': """
Inventory Report In-Out Excel
""",
    'description': """
Group By Product Category and Group By Location
""",
    "version": "1.1",
    "category": "stock",
    'author': "Matrix",
    'license': 'Other proprietary',
    "depends": [
        'point_of_sale',
        'sale_stock',
        'purchase_stock',
        'odoo_report_xlsx'
    ],
    "data": [
        'wizard/report_wizard_view.xml'
    ],
    "application": False,
    'installable': True,
    'price': 100,
    'sequence': 2,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],
}
