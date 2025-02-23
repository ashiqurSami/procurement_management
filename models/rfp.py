from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute
from ..utils.mail_utils import notify_approver_upon_recommended_rfq, notify_reviewer_upon_rfp_approval, \
    notify_supplier_upon_rfp_approval_and_publish, notify_reviewer_upon_rfp_rejection


class RFP(models.Model):
    _name="procurement_management.rfp"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _log_access = True
    _rec_name = 'rfp_id_seq'

    name=fields.Char(string='RFP Name')
    rfp_id_seq = fields.Char(
        string="RFP Reference",
        required=True, copy=False, readonly=True,
        index='trigram',
        default=lambda self: _('New'))

    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('recommended', 'Recommended'),
        ('accepted', 'Accepted')
    ], default='draft', tracking=True)

    required_date = fields.Date(
        string='Required Date',
        default=lambda self: fields.Date.add(fields.Date.today(), days=7)
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    approved_supplier = fields.Many2one(
        'res.partner',
        string='Approved Supplier',
        readonly=True
    )

    product_line_ids = fields.One2many(
        'procurement_management.rfp.product.line',
        'rfp_id',
        string='Product Lines'
    )

    selected_product_ids = fields.Many2many(
        'product.product',
        string='Selected Products',
        compute='_compute_selected_products',
    )

    @api.depends('product_line_ids.product_id')
    def _compute_selected_products(self):
        """
        Compute the selected product IDs based on the product lines.
        """
        for rfp in self:
            rfp.selected_product_ids = rfp.product_line_ids.mapped('product_id')

    rfq_line_ids = fields.One2many(
        'purchase.order',
        'rfp_id',
        string='RFQ Lines',
        domain=lambda self: self._get_rfq_domain()
    )
    total_amount=fields.Monetary(string='Total Amount')

    @api.model
    def _get_rfq_domain(self):
        user=self.env.user
        if user.has_group('procurement_management.group_procurement_management_approver'):
            return [('recommended','=',True)] if self.status in ['recommended','accepted'] else [('id', '=', False)]



    @api.model
    def create(self, vals):
        if vals.get('rfp_id_seq', _("New")) == _("New"):
            vals['rfp_id_seq'] = self.env['ir.sequence'].next_by_code(
                'rfp.id.sequence') or _("New")

        return super(RFP, self).create(vals)

    def action_submit(self):
        # Fetch the "Approver" group and its users
        self.write({'status': 'submitted'})
        approver_group = self.env['res.groups'].search([('name', '=', 'Approver')], limit=1)
        approver_group_users = approver_group.users

        # Fetch the email template
        template = self.env.ref('procurement_management.email_template_rfp_approval')

        context = {
            'name': self.name,
            'rfp_id': self.rfp_id_seq,
            'created_by': self.create_uid.name,
            'email_to' : self.env.user.company_id.email
        }
        print(self.create_uid.name,self.create_uid.id)
        # Send email to each approver
        for approver in approver_group_users:
            print(approver.email)
            if approver.email:
                template.with_context(**context).send_mail(approver.id)

    def action_recommend(self):
        if not any(line.recommended for line in self.rfq_line_ids):
            raise ValidationError(_(
                f"RFP {self.rfp_id_seq} cannot be marked as 'recommended' without at least one recommended RFQ."
            ))
        self.write({'status': 'recommended'})
        notify_approver_upon_recommended_rfq(self)

    def action_return_draft(self):
        self.status='draft'

    def action_approve(self):
        self.status='approved'
        notify_reviewer_upon_rfp_approval(self)
        notify_supplier_upon_rfp_approval_and_publish(self)

    def action_reject(self):
        self.status='rejected'
        notify_reviewer_upon_rfp_rejection(self)

    def action_close(self):
        self.status='closed'


    #
    # @api.depends('rfq_line_ids', 'rfq_line_ids.state')
    # def _compute_total_amount(self):
    #     for rfp in self:  # Iterate over each RFP in the recordset
    #         accepted_rfqs = rfp.rfq_line_ids.filtered(lambda l: l.state == 'purchase')
    #         total_amount = 0.0
    #         for rfq in accepted_rfqs:
    #             # Assuming tax_totals is a dictionary and contains 'amount_total'
    #             if rfq.tax_totals and 'amount_total' in rfq.tax_totals:
    #                 total_amount += rfq.tax_totals['amount_total']
    #         rfp.total_amount = total_amount



