# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Branches on Point of Sale',
    'version': '1.2',
    'summary': 'Multiple Branches management in Odoo POS',
    'sequence': 30,
    'description': """
        This application provide functionality of manage multi branches for Single Company.
        Multi Branches functionality covered in Point of Sale.
        Also maintain User and Manager level access rights.
    """,
    'category': 'Point of Sale',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['point_of_sale', 'multi_branches'],
    'data': [
        'security/pos_security.xml',
        'views/pos_config.xml',
    ],
    'demo': [],
    'qweb': [
         'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/main_screen.png'
    ],
    'price': 30.0,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}