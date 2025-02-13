from odoo import models, fields, api, exceptions,_

class PurchaseOrderLine(models.Model):
    _inherit="purchase.order.line"

    delivery_charge=fields.Float(string='Delivery Charge')

    # @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount','delivery_charge')
    # def _compute_amount(self):
    #     for line in self:
    #         tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
    #         totals = next(iter(tax_results['totals'].values()))
    #         amount_untaxed = totals['amount_untaxed']
    #         amount_tax = totals['amount_tax']

    #         line.update({
    #             'price_subtotal': amount_untaxed+line.delivery_charge,
    #             'price_tax': amount_tax,
    #             'price_total': amount_untaxed +amount_tax+line.delivery_charge,
    #         })

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'delivery_charge')
    def _compute_amount(self):
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = next(iter(tax_results['totals'].values()), {})
            
            amount_untaxed = totals.get('amount_untaxed', 0.0) + line.delivery_charge
            amount_tax = totals.get('amount_tax', 0.0)

            line.update({
                'price_subtotal': amount_untaxed,  # Include delivery charge here
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })
