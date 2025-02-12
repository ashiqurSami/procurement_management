from odoo import fields,api,models,_

def get_approver_group_users(env):
    approver_group = env['res.groups'].search([('name', '=', 'Approver')], limit=1)
    approver_group_users = approver_group.users
    return approver_group_users

def send_mail_to_reviewer_upon_quotation_submission(env, rfq):
    reviewer_group = env['res.groups'].sudo().search([('name', '=', 'Reviewer')], limit=1)
    reviewer_group_users = reviewer_group.users
    context = {
        'name': rfq.name,
        'partner_id': rfq.partner_id.id,
        'warranty_period': rfq.warranty_period,
        'expected_delivery_date': rfq.expected_delivery_date,
        'email_from': env.user.company_id.email
    }
    template = env.ref('procurement_management.email_template_to_notify_reviewer_upon_quotation_submission').sudo()
    for reviewer in reviewer_group_users:
        if reviewer.email:
            template.with_context(**context).send_mail(reviewer.id, force_send=True)

    def send_mail_to_approver_upon_recommended_rfq(env):
        approvers=get_approver_group_users(env)
        context={
            'name': env.rfp_id_seq,
            'expected_delivery_date': env.expected_delivery_date,
            'created_by': env.craete_uid.name,
            'recommended_by': env.write_uid.name,
            'email_from': env.user.company_id.email
        }
        template=env.ref('procurement_management.email_template_to_notify_approver_upon_recommended_rfq').sudo()
        for approver in approvers:
            if approver.email:
                template.with_context(**context).send_mail(approver.id, force_send=True)
