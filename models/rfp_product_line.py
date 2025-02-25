from odoo import fields,api,models,_

class RFPProductLine(models.Model):
    _name='procurement_management.rfp.product.line'


    product_id=fields.Many2one('product.product',
                               string='Product')
    description=fields.Text(string='Description')
    quantity=fields.Integer(string='Quantity')
    unit_price=fields.Monetary(string='Unit Price')
    delivery_charges=fields.Monetary(string='Delivery Charge')
    rfp_id = fields.Many2one('procurement_management.rfp', string='RFP')
    subtotal=fields.Monetary(string='Subtotal',
                             compute='_compute_subtotal',
                             currency_field='currency_id')
    currency_id = fields.Many2one(
        related='rfp_id.currency_id'
    )

    @api.depends('quantity','unit_price')
    def _compute_subtotal(self):
        for line in self:
           line.subtotal=line.quantity*line.unit_price+line.delivery_charges



    