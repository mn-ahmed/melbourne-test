# -*- coding: utf-8 -*-
{
    'name': "Damaged Product",
    'summary': """
        Sale Damaged Product Form""",
    'description': """
        Sale Damaged Product Form
    """,
    'author': "THA",
    'website': "http://www.asiamatrixsoftware.com",
    'category': 'Sale',
    'version': '3.4',
    'depends': ['sample_give_form', 'product_extend'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'reports/stock_damage_reports.xml',
        'reports/damage_issue_report.xml',
        'reports/damage_issue_report_template.xml',
        'reports/stock_damage_receipt_report_template.xml',
        'reports/stock_damage_delivery_report_template.xml',
        'views/damaged_form_view.xml',
        'views/stock_picking_view.xml',
    ],
}