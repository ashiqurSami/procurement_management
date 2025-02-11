from tokenize import String

from odoo import models, fields, api, exceptions,_
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('procurement_management.rfp', string='Linked RFP', readonly=True)
    expected_delivery_date = fields.Date()
    terms_conditions = fields.Html(string='Terms & Conditions')
    warranty_period = fields.Integer(string='Warranty (Months)')
    score = fields.Integer()
    recommended = fields.Boolean()
    rfp_status=fields.Selection(related='rfp_id.status',store=True,String="RFP Status")


    @api.constrains('recommended', 'partner_id', 'rfp_id')
    def _check_unique_recommended_per_supplier(self):
        """Ensure only one RFQ per supplier can be recommended within the same RFP."""
        for order in self:
            if order.recommended:
                existing_recommended = self.search([
                    ('rfp_id', '=', order.rfp_id.id),
                    ('partner_id', '=', order.partner_id.id),
                    ('recommended', '=', True),
                    ('id', '!=', order.id)  # Exclude the current record in case of updates
                ])
                if existing_recommended:
                    raise ValidationError(_(
                        f"A company {order.partner_id.name} cannot have more than one recommended RFQ for the same RFP {order.rfp_id.name}."
                    ))

    
