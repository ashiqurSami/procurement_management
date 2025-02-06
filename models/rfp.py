from odoo import models, fields, api,_

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
        ('recommendation', 'Recommendation'),
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
        string='RFQ Lines'
    )

    @api.model
    def create(self, vals):
        if vals.get('rfp_id_seq', _("New")) == _("New"):
            vals['rfp_id_seq'] = self.env['ir.sequence'].next_by_code(
                'rfp.id.sequence') or _("New")

        return super(RFP, self).create(vals)


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

