from tokenize import String
from odoo import models, fields, api, exceptions,_
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


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
        self.rfp_id.write({
            'status': 'accepted',
            'approved_supplier':self.partner_id.id,
            'total_amount':self.amount_total,
        })

        self.write({'state': 'purchase','date_approve':fields.Datetime.now()})
        # print("\n \n","self.rfp_id.rfq_line_ids",self.rfp_id.rfq_line_ids,"\n \n")
        cancelled_rfqs=self.env['purchase.order'].search([('rfp_id','=',self.rfp_id.id),('state','!=','purchase')])
        for rfq in cancelled_rfqs:
            rfq.write({'state':'cancel'})

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


    @api.depends_context('lang')
    @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed',
                 'order_line.delivery_charge')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)

            # Compute tax totals
            tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

            # Add delivery charge to tax totals
            total_delivery_charge = sum(order_lines.mapped('delivery_charge'))
            tax_totals['amount_untaxed'] += total_delivery_charge
            tax_totals['amount_total'] += total_delivery_charge

            order.tax_totals = tax_totals

    @api.model
    def get_supplier_metrics(self, supplier_id, date_range):
        date_from, date_to = self._get_date_range(date_range)

        orders = self.search([
            ("partner_id", "=", supplier_id),
            ("state", "=", "purchase"),
            ("date_order", ">=", date_from),
            ("date_order", "<=", date_to),
        ])

        total_amount = sum(orders.mapped("amount_total"))
        product_data = {}

        for order in orders:
            for line in order.order_line:
                product = line.product_id
                if product.name in product_data:
                    product_data[product.name]["quantity"] += line.product_qty
                else:
                    product_data[product.name] = {
                        "quantity": line.product_qty,
                        "image": product.image_1920.decode("utf-8") if product.image_1920 else "",
                    }

        return {
            "totalRFQs": len(orders),
            "totalAmount": total_amount,
            "productBreakdown": [{"name": k, "quantity": v["quantity"], "image": v["image"]} for k, v in product_data.items()],
        }


    def _get_date_range(self, date_range):
        today = fields.Date.today()
        if date_range == "this_week":
            start = today - timedelta(days=today.weekday())
        elif date_range == "last_week":
            start = today - timedelta(days=today.weekday() + 7)
        elif date_range == "last_month":
            start = today.replace(day=1) - timedelta(days=1)
            start = start.replace(day=1)
        elif date_range == "last_year":
            start = today.replace(month=1, day=1) - timedelta(days=1)
            start = start.replace(month=1, day=1)
        else:
            start = today  # Default fallback
        return start, today
