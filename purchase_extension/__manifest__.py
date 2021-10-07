{
    'name':
    'Purchase Extension',
    'sequence':
    3,
    'version':
    '13.2.2',
    'description':
    'Purchase Request Form and Invoice Format Extension',
    'summary':
    "Calculation of usage per day for purchase's products and format design for request form.",
    'category':
    'Purchase',
    'depends': ['purchase', 'purchase_stock', 'partner_code_generate'],
    'data': [
        'views/action_manager.xml',
        'report/purchase_report_view.xml',
        'wizard/po_list_by_vendor_wizard.xml',
        'wizard/po_payable_receivable_wizard.xml',
        'views/purchase_extend_view.xml',
    ],
    'installable':
    True,
    'application':
    True,
    'license':
    'OPL-1',
    'author':
    'Matrix',
}
