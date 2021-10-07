# -*- coding: utf-8 -*-
{
    'name': "Sale Excel Report",
    'summary': """
        Sale Excel Report""",
    'description': """
        Sale Excel Report by customer,brand and region(state)
    """,
    'author': "THA",
    'website': "http://www.asiamatrixsoftware.com",
    'category': 'Sale Reports',
    'version': '0.0.3',
    'depends': ['product_brand'],
    'data': [
        'wizard/sale_report_customer_view.xml',
        'wizard/sale_report_by_brand_view.xml',
        'wizard/sale_report_by_region_view.xml',
    ],
}