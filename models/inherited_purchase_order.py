from odoo import models, fields, api, exceptions,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('procurement_management.rfp', string='Linked RFP', readonly=True)
    expected_delivery_date = fields.Date()
    terms_conditions = fields.Html(string='Terms & Conditions')
    warranty_period = fields.Integer(string='Warranty (Months)')
    score = fields.Integer()
    recommended = fields.Boolean()


    # @api.constrains('recommended')
    # def _check_recommended(self):
    #     for rfq in self:
    #         if rfq.recommended and rfq.rfp_id.rfq_line_ids.filtered(lambda l: l.recommended and l.id != rfq.id):
    #             raise exceptions.ValidationError(_("Only one RFQ line can be recommended per RFP!"))
    #

