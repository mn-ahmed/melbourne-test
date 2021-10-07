# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Multi Branches Accounting Reports',
    'version': '1.0',
    'summary': 'Multi Branches Accounting Reports in Odoo',
    'sequence': 31,
    'description': """
        This application provide functionality of filter enterprise accounting reports and generate report by branches.
        Onscreen
        Reports
        Report
        Account report
        Accounting
        Branch
        Multi Branch
        Multi Branch Report
        Multi Branch Accounting Reports
Accounting
crm
sales
purchase
invoicing
inventory
stock
warehouse
voucher
multi branch
branch
Accounting multi branch
crm multi branch
sales multi branch
purchase multi branch
invoicing multi branch
stock multi branch
warehouse multi branch
multi branch report
multi branch accounting
multi branch account
multi branch accounting report
multi branch profit and loss
multi branch profit and loss report
multi branch balance sheet
balance sheet
profit and loss report
multi branch balance sheet report
multi branch cash flow
cash flow report
multi branch cash flow report
multi branch executive summary
multi branch check register
multi branch register
multi branch ledger
multi branch general ledger
multi branch partner ledger
multi branch aged receivable
multi branch aged payable
multi branch trial balance
multi branch tax report
multi branch branch wise report
branch wise report
tax report
trial balance
aged payable
ledger report
register
general ledger
receivable
cash flow statement
branch wise cash flow
branch wise cash flow statement
consolidated journals reports
partner Ledger
ledger report excel
partner ledger report excel
ledger report fiscal year
partner ledger report fiscal year
journal accounting entry
accounting entry
Financial Account report
Financial
Account
Financial account
income statement
profit and loss
aged partner balance
journal audit
financial report
account report
debit account
credit account
debit and credit account
credit and debit account
Asset
Tangible asset
Intangible asset
asset depreciation
depreciation
sell assets
dispose assets
assets report
assets journal entries
Account partner
Account balance
Account balance report
Aged partner balance report
aged partner report
account fiscal year
fiscal year
aged partner excel report
aged partner pdf report
Budget
Account Budget management
account budget
budget on project
budget on department
budget on company
budget on employee
income account
expense account
Tax
Account Tax Report
Advance filter
tax advance filter
account tax report on pdf
account tax report on excel
account sales tax report
account purchase tax report
sales tax
purchase tax
sales tax report
purchase tax report
account alert
account budget alert
account budget warning
account warning
warning
budget alert
budget warning
over budget alert
purchase warning
purchase alert
alert on purchase order
alert on purchase
purchase order alert
purchase order warning
warning on purchase order
warning on vendor bill
vendor bill warning
alert on vendor bill
vendor bill alert
Multi branches
company branches
branch on crm
branch on sales
branch on purchase
branch on account
branch on warehouse
branch on location
branch on stock operation
branch on stock
branch to branch transaction
stock move
stock move branch to branch
transfer stock branch to branch
stock transfer branch to branch
chart of account for branch
branch on picking
branch on vendor bills
inventory adjustment
inventory adjustment on branch
sales receipt branch wise
branch wise sales receipt
branch wise purchase receipt
branch wise journal entries
journal entries branch wise
branch wise payment
account journal
account journal audit
account journal audit report
account excel
account pdf
account audit
account audit report
account audit excel
account audit pdf
account journal excel
account journal pdf
account trial balance
account trial balance report
Trial balance report
trial balance period
trial balance comparison
account balance comparison
account trial balance report excel
account trial balance report pdf
trial balance report excel
trial balance report pdf
Analytic Account report
Analytic account
Analytic report
budget report
account budget report
multi level analytic report
multi level analytic account report
department budget
project budget
cost of project
cost of department
analytic account excel report
analytic account pdf report
excel report
pdf report
account excel report
account pdf report
Open Fiscal year
Close Fiscal year
Fiscal period
Cancel opening entry in fiscal year
Cancel closing entry in fiscal year
period
yearly
tax year
revenue
taxation
monetary
economy
circulate
financial year
journal entry
opening balance
closing balance
debt
profit & loss
agent
policy
imbalance
transparency
stance
effort
policies
year end
new year
company
audit
payment
customer
customer payment
customer payment overdue
overdue customer payment
customer overdue payment reminder
customer overdue payment follow up
mail
payment reminder mail
due days
payment due
due payment
scheduler
analysis
follow up analysis
Accounting & Auditing Terms
accounting concepts
financial management
marginal benefit
letter of credit
buyer
amount due
due amount
demand
cash
cash on delivery
deferred payment
duration
provision
cash flow
entrepreneur
monitoring
sale
feedback
requirement
effectiveness
following
auditing
management
contract management
payment term
warning/alert
vendor bill
Budgetary Positions
Planned Amount
Alert Types
budget limit
ignore
restrict
allow manager
purchase manager
account manager
purchase order
vendor bills
Odoo ERP Installation
Odoo ERP Migration
Digital Strategy
Odoo ERP configuration
Odoo ERP Staffing
Digital Technology Selection
Odoo ERP Customization
Odoo Functional Training
Digital Transformation Implementation
Odoo ERP New Module Development
Odoo ERP Technical Training
Legacy Modernization
Odoo ERP Integrations
Odoo ERP Support
Organizational Transformation
    """,
    'category': 'Sales/Accounting',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['account_accountant', 'account_reports', 'multi_branches'],
    'data': [
        'views/account_financial_report_asset.xml',
        'views/search_template_view.xml',
        'views/report_financial.xml'
        ],
    'demo': [],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'price': 80,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1'
}