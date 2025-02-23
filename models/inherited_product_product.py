from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     """
    #     Override name_search to filter out products already selected in the RFP.
    #     """
    #     if 'rfp_id' in self._context:
    #         rfp_id = self._context.get('rfp_id')
    #         rfp = self.env['procurement_management.rfp'].browse(rfp_id)
    #         selected_product_ids = rfp.selected_product_ids.ids
    #         args = args or []
    #         args.append(('id', 'not in', selected_product_ids))
    #     return super(ProductProduct, self).name_search(name, args, operator, limit)