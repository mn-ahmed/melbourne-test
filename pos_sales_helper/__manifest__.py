# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales Team, Sales Man and Helper on POS",
    'summary': """
Sales Team, Sales Man and Helper on POS
""",
    'description': """
Sales Team, Sales Man and Helper on POS
    """,
    "version": "1.2",
    "category": "Sales/Point Of Sale",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'point_of_sale',
        'hr',
        'sale',
    ],
    "data": [
        'views/pos_view.xml',
        'views/template.xml',
        'views/invoice_view.xml',
        'views/pos_config_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    "application": False,
    'installable': True,
}
