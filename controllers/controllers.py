# -*- coding: utf-8 -*-
import random
import base64
from odoo import api, http, modules,fields
from odoo.fields import Datetime
from odoo.http import request, Response
from datetime import datetime, timedelta




class ProcurementManagement(http.Controller):
    @http.route('/procurement_management/procurement_management', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/procurement_management/procurement_management/objects', auth='public')
    def list(self, **kw):
        return http.request.render('procurement_management.listing', {
            'root': '/procurement_management/procurement_management',
            'objects': http.request.env['procurement_management.procurement_management'].search([]),
        })

    @http.route('/procurement_management/procurement_management/objects/<model("procurement_management.procurement_management"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('procurement_management.object', {
            'object': obj
        })

    @http.route('/procurement_management/sign-up', auth='public',website=True)
    def sign_up(self, **kw):
        return request.render('procurement_management.sign_up_template',{})

    @http.route('/procurement_management/otp', auth='public', methods=['POST'], website=True)
    def send_otp(self, **kw):
        """
        Generates a One-Time Password (OTP) and sends it to the user's email address.
        """
        email = kw.get('email')
        error_list=[]
        success_list=[]

        if email:
            blacklisted = request.env['mail.blacklist'].sudo().search([('email', '=', email)])
            if blacklisted:
                error_list.append('This email is blacklisted. Please use another email.')

            already_exists = request.env['res.partner'].sudo().search([('email', '=', kw.get('email'))])
            if already_exists:
                error_list.append('This email is in already used. Please use another email.')

        if error_list:
            return request.render('procurement_management.sign_up_template',{'error_list':error_list})

        otp_code = random.randint(100000, 999999)
        expiry_time = datetime.now() + timedelta(days=5)

        otp_record = request.env['procurement_management.otp_verification'].sudo().create({
            'email': email,
            'otp': otp_code,
            'expiry_time': expiry_time
        })

        mail_values = {
            'subject': 'OTP code',
            'body_html': f'Your OTP is {otp_code}',
            'email_to': email,
            'email_from': 'samiashiqur@gmail.com'
        }

        mail_id = request.env['mail.mail'].sudo().create(mail_values)
        mail_id.sudo().send()
        success_list.append('OTP has been sent to your email.')

        # Pass the email to the OTP verification template
        return request.render('procurement_management.otp_verify_template', {
            'email': email,
            'success_list': success_list
        })

    @http.route('/procurement_management/verify', auth='public', methods=['POST','GET'], website=True)
    def verify_otp(self, **kw):
        """
        Verifies the OTP entered by the user.
        """
        email = kw.get('email')
        otp = kw.get('otp')
        error_list = []
        success_list=[]

        user = request.env['procurement_management.otp_verification'].sudo().search([
            ('email', '=', email),
            ('otp', '=', otp),
            ('is_verified', '=', False),
            ('expiry_time', '>', datetime.now())
        ], limit=1)

        if user:
            user.write({'is_verified': True})
            success_list.append('OTP verified. Proceeding to registration.')
            return request.render('procurement_management.supplier_registration_form_view_template', {
                'success_list': success_list
            })

        error_list.append('Invalid OTP. Please try again.')
        return request.render('procurement_management.otp_verify_template', {'error_list': error_list})

    @http.route('/procurement_management/register', auth='public', methods=['POST','GET'], website=True)
    def register_supplier(self, **kw):
        error_list = []
        success_list = []
        if request.httprequest.method == 'POST':
            vals = {}
            keys = [
                'company_name', 'email', 'phone', 'company_registered_address', 'company_alternate_address',
                'company_type_category', 'company_type', 'trade_license_number',
                'tax_identification_number', 'commencement_date', 'expiry_date',
                'contact_person_title', 'contact_email', 'contact_phone',
                'finance_contact_title', 'finance_contact_email', 'finance_contact_phone',
                'authorized_person_name', 'authorized_person_email', 'authorized_person_phone',
                'bank_name', 'bank_address', 'bank_swift_code', 'account_name',
                'account_number', 'iban', 'company_address_as_per_bank', 
                'client_1_name','client_1_address', 'client_1_contact_email','client_1_contact_phone', 
                'client_2_name','client_2_address','client_2_contact_email', 'client_2_contact_phone',
                'client_3_name','client_3_address', 'client_3_contact_email','client_3_contact_phone',
                'client_4_name','client_4_address', 'client_4_contact_email','client_4_contact_phone',
                'client_5_name','client_5_address', 'client_5_contact_email','client_5_contact_phone',
                'certification', 'certificate_number','certifying_body', 'award_date', 'certificate_expiry_date'
            ]
            for key in keys:
                if kw.get(key):
                    vals[key] = kw.get(key)

            for i in range(1,6):
                client_name=kw.get(f"client_{i}_name")
                client_address=kw.get(f"client_{i}_address")
                client_contact_email=kw.get(f"client_{i}_contact_email")
                client_contact_phone=kw.get(f"client_{i}_contact_phone")
                
                if (client_address or client_contact_email or client_contact_phone) and not client_name:
                    error_list.append(f'Client {i} name is madatory, if address, email or phone is provided')

            if kw.get('tax_identification_number') and (len(kw.get('tax_identification_number')) != 16 or not kw.get(
                    'tax_identification_number').isdigit()):
                error_list.append("Tax Identification Number Should Be Of 16 Digits And All Digits")
            if kw.get('trade_license_number') and not (8<=(len(kw.get('trade_license_number'))<13) or not kw.get(
                    'trade_license_number').isdigit()):
                error_list.append("Trade License Number Should Be Of 8-13 Digits And All Alphanumeric Digits")
            if kw.get('expiry_date') and fields.Date.to_date(kw.get('expiry_date')) <= fields.date.today():
                error_list.append("Expiry Date Should Be Greater Than Today")
            if not kw.get('company_name'):
                error_list.append("Company Name is mandatory")
            if not kw.get('email'):
                error_list.append("Company Email is mandatory")
            if kw.get('email'):
                already_exists = request.env['res.partner'].sudo().search([('email', '=', kw.get('email'))])
                if already_exists:
                    error_list.append("Company Email Already Exists In the system. Try with another email")
            file_fields = [
                'trade_license_business_registration', 'certificate_of_incorporation', 'certificate_of_good_standing',
                'establishment_card', 'vat_tax_certificate', 'memorandum_of_association',
                'identification_document_for_authorized_person', 'bank_letter_indicating_bank_account',
                'past_2_years_audited_financial_statements', 'other_certifications'
            ]

            file_vals = {}
            for field in file_fields:
                if kw.get(field):
                    file_vals[field] = base64.b64encode(kw.get(field).read())
            vals['state'] = 'submitted'
            if not error_list:
                # Create the supplier registration record
                new_supplier = request.env['procurement_management.supplier.registration'].sudo().create(vals)
                if new_supplier:
                    vals['state'] = 'submitted'
                    success_list.append("Supplier Registered Successfully")

                    # Fetch the "Reviewer" group and its users
                    reviewer_group = request.env['res.groups'].sudo().search([('name', '=', 'Reviewer')], limit=1)
                    reviewer_group_users = reviewer_group.users

                    # Fetch the email template
                    template = request.env.ref('procurement_management.email_template_form_submitted').sudo()
                    context={
                        'name':new_supplier.company_name,
                        'phone':new_supplier.phone,
                        'category':new_supplier.company_type_category
                    }

                    # Send email to each reviewer
                    for reviewer in reviewer_group_users:
                        print(reviewer.email)
                        print(reviewer.login)
                        if reviewer.email:
                            template.with_context(**context).send_mail(reviewer.id, force_send=True)


                if file_vals:
                    new_supplier.write(file_vals)

        return request.render("procurement_management.supplier_registration_form_view_template",
                              {'page_name': 'supplier_registration',
                               'error_list': error_list,
                               'success_list': success_list})


