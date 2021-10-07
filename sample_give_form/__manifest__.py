# -*- coding: utf-8 -*-
{
    'name': "Sample Give",
    'summary': """
        Sale Sample Give Form""",
    'description': """
        Sale Sample Give Form
    """,
    'author': "THA",
    'website': "http://www.asiamatrixsoftware.com",
    'category': 'Sale',
    'version': '2.7',
    'depends': ['sale','multi_branches','stock','stock_extend', 'product_extend'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'reports/sample_give_report_template.xml',
        'reports/sample_give_report.xml',
        'reports/stock_sample_reports.xml',
        'reports/stock_sample_delivery_report_template.xml',
        'reports/stock_sample_return_report_template.xml',
        'views/sample_give_views.xml',
        'views/stock_picking_view.xml',
    ],
}