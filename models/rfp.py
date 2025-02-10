from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class RFP(models.Model):
    _name="procurement_management.rfp"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _log_access = True
    _rec_name = 'rfp_id_seq'

    name=fields.Char(string='RFP Name',required=True)
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
    )

    product_line_ids = fields.One2many(
        'procurement_management.rfp.product.line',
        'rfp_id',
        string='Product Lines'
    )
    rfq_line_ids = fields.One2many(
        'purchase.order',
        'rfp_id',
        string='RFQ Lines',
        domain=lambda self: self._get_rfq_domain()
    )

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
                template.with_context(**context).send_mail(approver.id, force_send=True)

    def action_recommend(self):
        self.status='recommended'
        print(self)

    def action_return_draft(self):
        self.status='draft'

    def action_approve(self):
        self.status='approved'

    def action_reject(self):
        self.status='rejected'

    def action_close(self):
        self.status='closed'

    def action_accept(self):
        self.status='accepted'
        rfq=self.env['purchase.order'].search([('rfp_id','=',self.id)])
        # rfq.write({'state':'purchase'})
        rfq.button_confirm()
    

    # @api.constrains('status','rfq_line_ids')    
    # def _check_at_least_one_recommended_line(self):
    #         for rfp in self:
    #             if rfp.status in ('recommended','approved')  and not any(rfq.recommended for rfq in rfp.rfq_line_ids):
    #                 raise ValidationError(_(
    #                 f"RFP {rfp.rfp_id_seq} cannot be marked as '{rfp.status}' without at least one recommended RFQ."
    #             ))

    # @api.depends('rfq_line_ids.state', 'rfq_line_ids.amount_total')
    # def _compute_total_amount(self):
    #     for rfp in self:
    #         accepted_rfqs = rfp.rfq_line_ids.filtered(lambda l: l.state == 'accepted')
    #         rfp.total_amount = sum(accepted_rfqs.mapped('amount_total'))
    #
    # @api.depends('rfq_line_ids.recommended')
    # def _compute_recommended_suppliers(self):
    #     for rfp in self:
    #         rfp.recommended_suppliers = rfp.rfq_line_ids.filtered(
    #             lambda l: l.recommended
    #         ).mapped('partner_id')

