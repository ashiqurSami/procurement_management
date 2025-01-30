from odoo import api,fields,models,_

class OTPVerification(models.Model):
    _name='procurement_management.otp_verification'
    _description='OTP Verification'

    email=fields.Char(string='Email',required=True)
    otp=fields.Char(string='OTP',required=True)
    expiry_time=fields.Datetime(string='Expiry Time',required=True)
    is_verified=fields.Boolean(string='Is Verified',default=False)

