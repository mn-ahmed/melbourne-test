# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Multi Branches Reports',
    'version': '1.2',
    'summary': 'Multi Branches Reports in Odoo',
    'sequence': 31,
    'description': """
        This application provide functionality of manage multi branches for Single company.
        Multi Branches functionality covered in CRM, Sales, Purchase, Account, Warehouse and Locations, Inventory.
        Also maintain User and Manager level access rights.
        Generate report of Quotations, Sales, Purchases, Delivery receipt, Incoming shipment and Invoices branch wise.
    """,
    'category': 'Sales/Accounting',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['multi_branches'],
    'data': [
        'report/account_template.xml',
        'report/sale_templates.xml',
        'report/stock_template.xml',
        'report/purchase_template.xml',
        ],
    'demo': [],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'price': 120.0,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}
