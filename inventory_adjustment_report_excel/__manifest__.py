{
    'name': 'Inventory Adjustment Report Excel',
    'version': '0.2',
    'category': 'Report',
    'sequence': 100,
    'summary': 'Inventory Adjustment Report Excel',
    'description': """
Report Customization Module
==================================
    """,
    'author': 'asiamatrix',
    'website': 'http://www.asiamatrixsoftware.com',
    'images': [],
    'depends': ['base',],
    'data': [   
        'wizard/invnetory_adjustment_report_wizard.xml',  
        'security/ir.model.access.csv',         
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
