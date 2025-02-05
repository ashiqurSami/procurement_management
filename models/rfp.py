from odoo import models, fields, api

class RFP(models.Model):
    _name="procurement_management.rfp"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _log_access = True

    name = fields.Char(
        string='RFP Number',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('procurement.rfp.seq')
    )

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
    recommended_suppliers = fields.Many2many(
        'res.partner',
        compute='_compute_recommended_suppliers'
    )

    approved_supplier = fields.Many2one(
        'res.partner',
        string='Approved Supplier',
        domain="[('id', 'in', recommended_suppliers)]"
    )

    product_line_ids = fields.One2many(
        'procurement.rfp.product.line',
        'rfp_id',
        string='Product Lines'
    )
    rfq_line_ids = fields.One2many(
        'purchase.order',
        'rfp_id',
        string='RFQ Lines'
    )


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