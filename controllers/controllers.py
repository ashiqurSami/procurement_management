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

    @http.route('/procurement_management/otp',auth='public',methods=['POST'],website=True)
    def send_otp(self,**kw):
        """"
        Generates a One-Time Password (OTP) and sends it to the user's email address.
        This function performs the following steps:
        1. Retrieves the email address from the request parameters.
        2. Checks if the email address is blacklisted.
        3. If the email is not blacklisted, generates a random 6-digit OTP.
        4. Sets an expiry time for the OTP (5 days from the current time).
        5. Creates an email with the OTP and sends it to the specified email address.

        Args:
            **kw: Arbitrary keyword arguments containing the request parameters.
        Returns:
            str: A success message if the OTP is sent successfully.
            dict: An error message if the email is blacklisted.
        """
        email=kw.get('email')

        blacklisted=request.env['mail.blacklist'].sudo().search([('email','=',email)])
        if blacklisted:
            return {
                'status':'error',
                'message':'This email is blacklisted'
            }
        otp_code=random.randint(100000,999999)
        expiry_time=datetime.now()+timedelta(days=5)

        mail_values={
            'subject':'OTP code',
            'body_html':f'Your OTP is {otp_code}',
            'email_to':email,
            'email_from':'samiashiqur@gmail.com'
        }

        mail_id=request.env['mail.mail'].sudo().create(mail_values)
        mail_id.sudo().send()

        return 'otp sent successfull'
