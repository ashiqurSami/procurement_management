# -*- coding: utf-8 -*-
{
    'name': "procurement_management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # Dependencies
    'depends': ['base', 'portal', 'purchase', 'account', 'contacts', 'mail'],

    # Always loaded
    'data': [
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/procurement_management_portal.xml',
        'views/supplier_registration_views.xml',
        'views/res_partner_bank_inherit_views.xml',
        'views/res_partner_extended.xml',
        'views/bank_views_extended.xml',
        'views/rfp_views.xml',
        'views/ir_sequence.xml',
        'views/dashboard_views.xml',
        'wizard/supplier_reject_blacklist_wizard.xml',
        'views/email_templates.xml',
        'views/purchase_order_inherit_views.xml',
        'wizard/rfp_report_wizard.xml',
        'views/procurement_management_menus.xml',
    ],

    # Only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'procurement_management/static/src/js/dashboard.js',  # OWL Component
            'procurement_management/static/src/xml/dashboard.xml',  # QWeb template
        ],
    },
}
