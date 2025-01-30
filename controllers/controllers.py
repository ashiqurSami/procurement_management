# -*- coding: utf-8 -*-
import random

from odoo import api, http, modules
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

        blacklisted = request.env['mail.blacklist'].sudo().search([('email', '=', email)])
        if blacklisted:
            return {
                'status': 'error',
                'message': 'This email is blacklisted'
            }

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

        # Pass the email to the OTP verification template
        return request.render('procurement_management.otp_verify_template', {'email': email})

    @http.route('/procurement_management/verify', auth='public', methods=['POST','GET'], website=True)
    def verify_otp(self, **kw):
        """
        Verifies the OTP entered by the user.
        """
        email = kw.get('email')
        otp = kw.get('otp')

        user = request.env['procurement_management.otp_verification'].sudo().search([
            ('email', '=', email),
            ('otp', '=', otp),
            ('is_verified', '=', False),
            ('expiry_time', '>', datetime.now())
        ], limit=1)

        if user:
            user.write({'is_verified': True})
            return 'OTP verified successfully'

        return 'OTP verification failed'


