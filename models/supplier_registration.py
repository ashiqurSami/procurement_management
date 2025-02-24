# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SupplierRegistration(models.TransientModel):
    _name = 'procurement_management.supplier.registration'
    _description = 'Supplier Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'company_name'
    _order = 'create_date desc'

    company_name = fields.Char(string='Company Name')
    email = fields.Char(string='Company Email')
    phone = fields.Char(string='Company Phone')
    company_address = fields.Char(string='Company Registered Address')
    company_logo=fields.Binary(string="Company Logo")
    company_type_category = fields.Selection([
        ('LLC', 'LLC'),
        ('corporate', 'Corporation'),
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('cooperative', 'Cooperative')
    ], string='Company Category')
    trade_license_number = fields.Char(string='Trade License Number')
    tax_identification_number = fields.Char(string='Tax Identification Number')
    commencement_date = fields.Date(string='Commencement Date')
    expiry_date = fields.Date(string='Expiry Date')

    #primary_contact_person
    contact_person_title = fields.Char(string='Contact Person Title')
    contact_email = fields.Char(string='Contact Email')
    contact_phone = fields.Char(string='Contact Phone')
    contact_address = fields.Char(string='Contact Address')

    #finance_contact_person
    finance_contact_title = fields.Char(string='Finance Contact Title')
    finance_contact_email = fields.Char(string='Finance Contact Email')
    finance_contact_phone = fields.Char(string='Finance Contact Phone')
    finance_contact_address = fields.Char(string='Finance Contact Address')

    #authorized_contact_person
    authorized_person_name = fields.Char(string='Authorized Person Name')
    authorized_person_email = fields.Char(string='Authorized Person Email')
    authorized_person_phone = fields.Char(string='Authorized Person Phone')
    authhorized_person_address = fields.Char(string='Authorized Person Address')

    #bank_details
    bank_name = fields.Char(string='Bank Name')
    bank_address = fields.Char(string='Bank Address')
    bank_swift_code = fields.Char(string='Bank Swift Code')
    account_name = fields.Char(string='Account Name')
    account_number = fields.Char(string='Account Number')
    iban = fields.Char(string='IBAN')


    company_address_as_per_bank = fields.Char(string='Company Address as per Bank') #it might not be needed

    #client_1
    client_1_name = fields.Char(string='Client 1 Name')
    client_1_address = fields.Char(string='Client 1 Address')
    client_1_contact_email = fields.Char(string='Client 1 Contact Email')
    client_1_contact_phone = fields.Char(string='Client 1 Contact Phone')

    #client_2
    client_2_name = fields.Char(string='Client 2 Name')
    client_2_address = fields.Char(string='Client 2 Address')
    client_2_contact_email = fields.Char(string='Client 2 Contact Email')
    client_2_contact_phone = fields.Char(string='Client 2 Contact Phone')

    #client_3
    client_3_name = fields.Char(string='Client 3 Name')
    client_3_address = fields.Char(string='Client 3 Address')
    client_3_contact_email = fields.Char(string='Client 3 Contact Email')
    client_3_contact_phone = fields.Char(string='Client 3 Contact Phone')

    #client_4
    client_4_name = fields.Char(string='Client 3 Name')
    client_4_address = fields.Char(string='Client 3 Address')
    client_4_contact_email = fields.Char(string='Client 3 Contact Email')
    client_4_contact_phone = fields.Char(string='Client 3 Contact Phone')

    #client_5
    client_5_name = fields.Char(string='Client 3 Name')
    client_5_address = fields.Char(string='Client 3 Address')
    client_5_contact_email = fields.Char(string='Client 3 Contact Email')
    client_5_contact_phone = fields.Char(string='Client 3 Contact Phone')

    #certifications
    certification = fields.Char(string='Certification')
    certificate_number = fields.Char(string='Certificate Number')
    certifying_body = fields.Char(string='Certifying Body')
    award_date = fields.Date(string='Award Date')
    certificate_expiry_date = fields.Date(string='Certificate Expiry Date')

    #document submission
    trade_license_business_registration = fields.Binary(string='Trade License/Business Registration')
    certificate_of_incorporation = fields.Binary(string='Certificate of Incorporation')
    certificate_of_good_standing = fields.Binary(string='Certificate of Good Standing')
    establishment_card = fields.Binary(string='Establishment Card')
    vat_tax_certificate = fields.Binary(string='VAT/TAX Certificate')
    memorandum_of_association = fields.Binary(string='Memorandum of Association')
    identification_document_for_authorized_person = fields.Binary(string='Identification Document for Authorized Person')
    bank_letter_indicating_bank_account = fields.Binary(string='Bank Letter indicating Bank Account')
    past_2_years_audited_financial_statements = fields.Binary(string='Past 2 Years Audited Financial Statements')
    other_certifications = fields.Binary(string='Other Certifications')

    reviewer_id = fields.Many2one('res.users', string='Reviewed By')
    approver_id=fields.Many2one('res.users',string='Approved By')
    comments=fields.Text(string="Comments")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed','Reviewed') ,
        ('rejected', 'Rejected'),
        ('blacklisted','Blacklisted'),
        ('approved', 'Approved')],
        string='State', default='draft')

    def action_approve(self):
        vals = {
            'name': self.company_name or 'N/A',
            'email': self.email or 'N/A',
            'phone': self.phone or 'N/A',
            'image_1920':self.company_logo.decode('utf-8'),
            'street': self.company_address or 'N/A',
            'company_type_category': self.company_type_category or 'N/A',
            'trade_license_number': self.trade_license_number or 'N/A',
            'vat': self.tax_identification_number or 'N/A',
            'commencement_date': self.commencement_date or fields.Date.today(),
            'expiry_date': self.expiry_date or fields.Date.today(),
            'certification': self.certification or 'N/A',
            'certificate_number': self.certificate_number or 'N/A',
            'certifying_body': self.certifying_body or 'N/A',
            'award_date': self.award_date or 'N/A',
            'certificate_expiry_date': self.certificate_expiry_date or 'N/A',
            'supplier_rank': 1,
            'company_type': 'company',
        }
        vals = {k: v for k, v in vals.items() if v != 'N/A'}
        vals['child_ids'] = []
        vals['bank_ids'] = []
        if self.contact_person_title:
            vals['child_ids'].append((0, 0, {
                'name': self.contact_person_title,
                'email': self.contact_email,
                'phone': self.contact_phone,
                'type': 'contact',
            }))
        if self.authorized_person_name:
            vals['child_ids'].append((0, 0, {
                'name': self.authorized_person_name,
                'email': self.authorized_person_email,
                'phone': self.authorized_person_phone,
                'type': 'contact',
            }))
        if self.finance_contact_title:
            vals['child_ids'].append((0, 0, {
                'name': self.finance_contact_title,
                'email': self.finance_contact_email,
                'phone': self.finance_contact_phone,
                'type': 'contact',
            }))
        for client in range(1, 6):
            client_name = getattr(self, f'client_{client}_name', None)
            client_address = getattr(self, f'client_{client}_address', None)
            client_email = getattr(self, f'client_{client}_contact_email', None)
            client_phone = getattr(self, f'client_{client}_contact_phone', None)
            if client_name:
                vals['child_ids'].append((0, 0, {
                    'name': client_name,
                    'email': client_email,
                    'phone': client_phone,
                    'street': client_address,
                    'type': 'contact',
                }))

        if self.bank_name:
            bank_id = self.env['res.bank'].create({
                'name': self.bank_name,
                'street': self.bank_address,
                'bank_swift_code': self.bank_swift_code,
                'iban': self.iban,
            })
            vals['bank_ids'].append((0, 0, {
                'bank_id': bank_id.id,
                'acc_number': self.account_number,
                'acc_holder_name': self.account_name,
                'address': self.company_address_as_per_bank,
            }))
            # Check for file fields and add them to vals if present
        file_fields = [
            'trade_license_business_registration',
            'certificate_of_incorporation',
            'certificate_of_good_standing',
            'establishment_card',
            'vat_tax_certificate',
            'memorandum_of_association',
            'identification_document_for_authorized_person',
            'bank_letter_indicating_bank_account',
            'past_2_years_audited_financial_statements',
            'other_certifications'
        ]
        for field in file_fields:
            if getattr(self, field):
                vals[field] = getattr(self, field)
        new_supplier = self.env['res.partner'].create(vals)
        new_user = self.env['res.users'].create({
            'login': self.email,
            'password': self.phone,
            'partner_id': new_supplier.id,
            'company_id': self.env.company.id,
            'groups_id': [(6, 0, self.env.ref('base.group_portal').ids)]
        })
        self.env.ref('procurement_management.email_template_vendor_registration_confirmation').send_mail(new_supplier.id)
        self.state = 'approved'
        self.approver_id=self.env.user

    def action_reject_or_blacklist(self):
        action_type="Blacklisting" if self.env.context.get('blacklisted') else "Rejection"

        action=self.env.ref('procurement_management.supplier_reject_blacklist_wizard_action').read()[0]
        action['name']=f'{action_type} Reason'
        return action

    def action_submit(self):
        self.state = 'submitted'

    def action_recommend(self):
        self.reviewer_id=self.env.user
        self.state="reviewed"

