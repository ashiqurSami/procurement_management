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


    def action_accept(self):
        self.rfp_id.write({'status': 'accepted','approved_supplier':self.partner_id.id,'total_amount':self.amount_total})
        self.write({'state': 'purchase','date_approve':fields.Datetime.now()})
        print(self.rfp_id.rfq_line_ids)
        return{
            'type':'ir.actions.act_window',
            'res_model':'procurement_management.rfp',
            'view_mode':'form',
            'res_id':self.rfp_id.id,
            'target':'current',
        }
            
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
 
    
    @api.depends('order_line.price_total', 'order_line.delivery_charge')
    def _amount_all(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))  # price_subtotal already includes delivery charge
                amount_tax = sum(order_lines.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax
