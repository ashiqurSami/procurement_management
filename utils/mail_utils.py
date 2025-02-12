from odoo import fields,api,models,_

def get_approver_group_users(self):
    approver_group = self.env['res.groups'].search([('name', '=', 'Approver')], limit=1)
    approver_group_users = approver_group.users
    return approver_group_users

def send_mail_to_reviewer_upon_quotation_submission(env, rfq):
    reviewer_group = env['res.groups'].sudo().search([('name', '=', 'Reviewer')], limit=1)
    reviewer_group_users = reviewer_group.users
    context = {
        'name': rfq.name,
        'partner_id': rfq.partner_id.name,
        'warranty_period': rfq.warranty_period,
        'expected_delivery_date': rfq.expected_delivery_date,
        'email_from': env.user.company_id.email,
        'rfp_id': rfq.rfp_id.rfp_id_seq
    }
    template = env.ref('procurement_management.email_template_to_notify_reviewer_upon_quotation_submission').sudo()
    for reviewer in reviewer_group_users:
        if reviewer.email:
            template.with_context(**context).send_mail(reviewer.id, force_send=True)

def send_mail_to_approver_upon_recommended_rfq(self):
    approvers=get_approver_group_users(self)
    context={
        'name': self.rfp_id_seq,
        'created_by': self.create_uid.name,
        'recommended_by': self.write_uid.name,
        'email_from': self.env.user.company_id.email
    }
    template=self.env.ref('procurement_management.email_template_to_notify_approver_upon_recommended_rfq').sudo()
    for approver in approvers:
        if approver.email:
            template.with_context(**context).send_mail(approver.id, force_send=True)
