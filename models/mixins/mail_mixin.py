from addons.account.models.chart_template import template
from odoo import fields,api,models,_

class MailMixin(models.AbstractModel):
    _name='mail.mixin'
    _description = 'Mixin to send mail'

    def send_mail_to_reviewer_upon_quotation_submission(self,rfq):
        reviewer_group = self.env['res.groups'].sudo().search([('name', '=', 'Reviewer')], limit=1)
        reviewer_group_users = reviewer_group.users
        context={
            'name': rfq.name,
            'partner_id': rfq.partner_id.id,
            'warranty_period': rfq.warranty_period,
            'expected_delivery_date': rfq.expected_delivery_date,
            'email_from': self.env.user.company_id.email
        }
        template=self.env.ref('procurement_management.email_template_to_notify_reviewer_upon_quotation_submission').sudo()
        for reviewer in reviewer_group_users:
            if reviewer.email:
                template.with_context(**context).send_mail(reviewer.id, force_send=True)