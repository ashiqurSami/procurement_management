from odoo import fields,api,models,_
from odoo.cli.scaffold import template
from odoo.conf import server_wide_modules


def get_approver_group_users(self):
    approver_group = self.env['res.groups'].sudo().search([('name', '=', 'Approver')], limit=1)
    approver_group_users = approver_group.users
    return approver_group_users

def get_reviewer_group_users(self):
    reviewer_group = self.env['res.groups'].sudo().search([('name', '=', 'Reviewer')], limit=1)
    reviewer_group_users = reviewer_group.users
    return reviewer_group_users

def get_reviewer(self):
    reviewers = get_reviewer_group_users(self)
    reviewer = reviewers.filtered(lambda user: user.id == self.create_uid.id)
    return reviewer

def notify_reviewer_upon_quotation_submission(self, rfq):
    reviewer_group_users = get_reviewer_group_users(self)
    context = {
        'name': rfq.name,
        'partner_id': rfq.partner_id.name,
        'warranty_period': rfq.warranty_period,
        'expected_delivery_date': rfq.expected_delivery_date,
        'email_from': self.env.user.company_id.email,
        'rfp_id': rfq.rfp_id.rfp_id_seq
    }
    template = self.env.ref('procurement_management.email_template_to_notify_reviewer_upon_quotation_submission').sudo()
    for reviewer in reviewer_group_users:
        if reviewer.email:
            template.with_context(**context).send_mail(reviewer.id, force_send=True)

def notify_approver_upon_recommended_rfq(self):
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

def notify_reviewer_upon_rfp_approval(self):
    reviewer = get_reviewer(self)
    context={
        'rfp_id': self.rfp_id_seq,
        'email_to': reviewer.email,
        'email_from': self.env.user.company_id.email,
        'approved_by':self.env.user.name,
        'created_by':self.create_uid.name
    }
    template=self.env.ref('procurement_management.email_template_to_notify_reviewer_upon_rfp_approval').sudo()
    template.with_context(**context).send_mail(reviewer.id, force_send=True)


def notify_supplier_upon_rfp_approval_and_publish(self):
    vendors = self.env['res.partner'].search([
        ('supplier_rank', '>', 0),
        ('active', '=', True)  # Optional: exclude archived
    ])
    context={
        'rfp_id': self.rfp_id_seq,
        'email_from': self.env.user.company_id.email,
        'required_date': self.required_date,
    }
    template=self.env.ref('procurement_management.email_template_to_notify_supplier_upon_rfp_publish_and_approval').sudo()
    for vendor in vendors:
        if vendor.email:
            template.with_context(**context).send_mail(vendor.id, force_send=True)

def notify_reviewer_upon_rfp_rejection(self):
    reviewer=get_reviewer(self)
    context={
        'rfp_id': self.rfp_id_seq,
        'email_from': self.env.user.company_id.email,
    }
    template=self.env.ref('procurement_management.email_template_to_notify_reviewer_upon_rfp_rejection').sudo()
    template.with_context(**context).send_mail(reviewer.id, force_send=True)

