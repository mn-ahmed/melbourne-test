# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Location From Order to Picking and Invoice",
    'summary': """
Location From Order to Picking and Invoice
""",
    'description': """
Location From Order to Picking and Invoice
Module allow to pass locations as below:

- Destination Location: Purchase Order -> Vendor Bill -> Incoming Shipment
- Source Location : Sale Order -> Customer Invoice -> Delivery Order
    """,
    "version": "0.1",
    "category": "Purchases",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'account',
        'purchase_stock',
        'sale_stock'
    ],
    "data": [
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/invoice_view.xml'
    ],
    "application": False,
    'installable': True,
}
