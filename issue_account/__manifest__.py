{
    'name': 'Issue Account',

    'version': '0.3',

    'description': 'Issue Account Customization',

    'summary': "issue account is added at the sample and damage. This account will be defined issue account at the stock Journal.",

    'category': 'Sale',

    'depends': ['sale', 'account', 'sample_give_form', 'damage_form'],

    'data': [
        'views/res_config_settings.xml',
        'views/issue_extend_views.xml',
    ],

    'installable': True,

    'application': True,

}
