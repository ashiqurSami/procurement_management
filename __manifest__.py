# -*- coding: utf-8 -*-
{
    'name': "procurement_management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'purchase', 'account', 'contacts','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/procurement_management_portal.xml',
        'views/supplier_registration_views.xml',
        'views/res_partner_bank_inherit_views.xml',
        'views/res_partner_extended.xml',
        'views/bank_views_extended.xml',
        'views/procurement_management_menus.xml',
        'wizard/supplier_reject_blacklist_wizard.xml',
        'views/email_templates.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

