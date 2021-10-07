# -*- coding: utf-8 -*-
{
    'name': 'Bill Of Landing',

    'version': '0.3',

    'summary': 'Added bill of landing form',

    'description': """
       * Added bill of landing form in purchase module.
    """,

    'category': 'Purchase',

    'Author': 'Asia Matrix Software Solution',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'base_customer_supplier',
        'product_brand',
        'purchase',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/bill_of_landing_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
