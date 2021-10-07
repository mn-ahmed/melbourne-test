# -*- coding: utf-8 -*-
{
    'name': 'Account Currency Rate',

    'version': '0.1',

    'summary': 'Multi Currency Rate',

    'description': """
       * Added base currency rate field.
       * Automatically compute rate.
       * This module using base currency MMK.  
    """,

    'category': 'Account',

    'website': "www.asiamatrixsoftware.com",

    'email': 'info@asiamatrixsoftware.com',

    'depends': [
        'base',
    ],

    'data': [
        'views/res_currency_views.xml',
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
