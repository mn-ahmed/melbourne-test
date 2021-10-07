# -*- coding: utf-8 -*-
{
    'name': 'Base Contact Myanmar',

    'version': '1.4',

    'summary': 'Added township selection field',

    'description': """
       * Added township selection field in contact form. 
    """,

    'category': 'Contact',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'base',
        'contacts',
    ],

    'data': [
        'data/res_country_data.xml',
        'security/ir.model.access.csv',
        'views/res_city_views.xml',
        'views/res_township_views.xml',
        'views/res_partner_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
