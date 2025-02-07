from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class MyRFQPortal(CustomerPortal):
    @http.route(['/procurement_management/rfps', '/procurement_management/rfps/page/<int:page>'], type='http',
                auth='user', website=True)
    def rfps_list(self, page=1, sortby=None, search=None, search_in='all', groupby='none', **kw):
        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('RFP Name'), 'order': 'name'},
            'status': {'label': _('Status'), 'order': 'status'},
            'required_date': {'label': _('Required Date'), 'order': 'required_date'},
        }

        # Searching options
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'name': {'label': _('RFP Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]},
            'rfp_id_seq': {'label': _('RFP Reference'), 'input': 'rfp_id_seq',
                           'domain': [('rfp_id_seq', 'ilike', search)]}
        }

        # Apply search filters
        search_domain = search_list[search_in]['domain'] if search and search_in in search_list else []

        # Add condition to only include accepted RFPs
        search_domain.append(('status', '=', 'approved'))

        # Default sorting
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not groupby or groupby == 'none':
            groupby = 'status'
        # Grouping options
        groupby_list = {
            'none': {'label': _('None'), 'input': ''},
            'status': {'label': _('Status'), 'input': 'status'},
            'required_date': {'label': _('Required Date'), 'input': 'required_date'},
        }

        # Ensure group_by_rfp is always a dictionary
        group_by_rfp = groupby_list.get(groupby, {'input': None})

        # Pagination setup
        rfp_obj = request.env['procurement_management.rfp']
        rfp_count = rfp_obj.search_count(search_domain)
        items_per_page = 3  # Adjust as needed
        pager = portal_pager(
            url='/procurement_management/rfps',
            total=rfp_count,
            page=page, step=items_per_page,
            scope=5,
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby}
        )

        # Fetch paginated records
        rfps = rfp_obj.search(search_domain, limit=items_per_page, offset=pager['offset'], order=order)

        # Grouping logic
        if group_by_rfp['input']:  # Only group if valid input is provided
            rfp_group_list = [{group_by_rfp['input']: key, 'rfps': list(group)}
                              for key, group in groupbyelem(rfps, itemgetter(group_by_rfp['input']))]
        else:
            rfp_group_list = [{'rfps': rfps}]

        return request.render('procurement_management.rfp_list_view_template', {
            'group_rfps': rfp_group_list,
            'page_name': 'my_rfp',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'default_url': '/my/rfps',
            'groupby': groupby,
            'searchbar_groupby': groupby_list,
        })

    @http.route('/procurement_management/rfp/<int:rfp_id>', auth='user', methods=['POST', 'GET'], website=True)
    def rfp_details(self,rfp_id,**kw):
        rfp=request.env['procurement_management.rfp'].sudo().browse(rfp_id)
        return request.render('procurement_management.rfp_form_view_template',{'rfp':rfp})

    @http.route(['/procurement_management/rfp/<int:rfp_id>/create_rfp'], type='http',auth='user', website=True)
    def create_rfq(self,rfp_id,**kw):
        print(request.env.user.partner_id.id, request.env.user.id)
        print(kw)
        rfp=request.env['procurement_management.rfp'].sudo().browse(rfp_id)

        return request.rende('procurement_management.rfq_submit_view_template',{'rfp':rfp})

    @http.route(['/procurement_management/rfp/<int:rfp_id>/submit'], type='http', auth='user',methods=['POST'] ,website=True)
    def rfp_submit(self, rfp_id, **kw):
        error_list=[]
        success_list=[]
        print(request.env.user.partner_id.id, request.env.user.id)
        print(kw)
        rfp=request.env['procurement_management.rfp'].sudo().browse(rfp_id)

        rfq_values={
            'rfp_id': rfp.id,
            'partner_id': request.env.user.partner_id.id,
            'warranty_period': kw.get('warranty_period'),
        }
        rfq=request.env['purchase.order'].sudo().create(rfq_values)
        success_list.append('RFQ submitted successfully.')

        for line in rfp.product_line_ids:
            rfq_line={
                'order_id':rfq.id,
                'product_id':line.product_id.id,
                'name':line.product_id.name,
                'price_unit':kw.get(f'order_line_quantity_{line.id}'),
                'product_qty':kw.get(f'order_line_unit_price_{line.id}')
            }
            request.env['purchase.order.line'].sudo().create(rfq_line)

        return request.render('procurement_management.rfq_submit_view_template',{'rfp':rfp,'success_list':success_list})



 