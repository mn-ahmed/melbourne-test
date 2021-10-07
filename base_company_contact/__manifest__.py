# -*- coding: utf-8 -*-
{
    'name': 'Base Company Contact',

    'version': '1.1',

    'summary': 'Added township selection field',

    'description': """
       * Added township selection field in contact form. 
    """,

    'category': 'Company',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'base_contact_myanmar',
    ],

    'data': [
        'views/res_company_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
