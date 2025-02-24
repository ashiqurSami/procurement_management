from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
from ..utils.mail_utils import notify_reviewer_upon_quotation_submission
from odoo.osv import expression
from datetime import datetime


class MyRFQPortal(CustomerPortal):
    @http.route(['/procurement_management/rfps', '/procurement_management/rfps/page/<int:page>'], type='http',
                auth='user', website=True)
    def rfps_list(self, page=1, sortby=None, search=None, search_in='all', groupby='none', **kw):
        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'required_date': {'label': _('Required Date'), 'order': 'required_date'},
            'rfp_id_seq': {'label': _('RFP Reference'), 'order': 'rfp_id_seq'},
        }

        # Searching options
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'rfp_id_seq': {'label': _('RFP Reference'), 'input': 'rfp_id_seq',
                           'domain': [('rfp_id_seq', 'ilike', search)]}
        }

        # Default search domain (only approved RFPs)
        search_domain = [('status', '=', 'approved')]

        # Apply search filters if search and search_in are provided
        if search and search_in in search_list:
            search_domain += search_list[search_in]['domain']

        # Default sorting
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Grouping options
        groupby_list = {
            'none': {'label': _('None'), 'input': ''},
            'required_date': {'label': _('Required Date'), 'input': 'required_date'},
        }

        # Ensure groupby is valid
        if groupby not in groupby_list:
            groupby = 'none'

        # Pagination setup
        rfp_obj = request.env['procurement_management.rfp']
        rfp_count = rfp_obj.search_count(search_domain)
        items_per_page = 5  # Adjust as needed
        pager = portal_pager(
            url='/procurement_management/rfps',
            total=rfp_count,
            page=page,
            step=items_per_page,
            scope=5,
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby}
        )

        # Fetch paginated records
        rfps = rfp_obj.search(search_domain, limit=items_per_page, offset=pager['offset'], order=order)

        # Grouping logic
        group_by_rfp = groupby_list[groupby]
        if group_by_rfp['input']:  # Only group if valid input is provided
            rfp_group_list = [{group_by_rfp['input']: key, 'rfps': list(group)}
                              for key, group in groupbyelem(rfps, itemgetter(group_by_rfp['input']))]
        else:
            rfp_group_list = [{'rfps': rfps}]

        return request.render('procurement_management.rfp_list_view_template', {
            'group_rfps': rfp_group_list,
            'page_name': 'rfp',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'default_url': '/procurement_management/rfps',
            'groupby': groupby,
            'searchbar_groupby': groupby_list,
        })

    @http.route('/procurement_management/rfp/<int:rfp_id>', auth='user', methods=['POST', 'GET'], website=True)
    def rfp_details(self,rfp_id,**kw):
        rfp=request.env['procurement_management.rfp'].sudo().browse(rfp_id)
        return request.render('procurement_management.rfp_form_view_template',{'rfp':rfp,'page_name':'rfp_id'})

    @http.route(['/procurement_management/rfp/<int:rfp_id>/create_rfp'], type='http',auth='user', website=True)
    def create_rfq(self,rfp_id,**kw):
        print(request.env.user.partner_id.id, request.env.user.id)
        print(kw)
        rfp=request.env['procurement_management.rfp'].sudo().browse(rfp_id)

        return request.render('procurement_management.rfq_submit_view_template',{'rfp':rfp})

    @http.route(['/procurement_management/rfp/<int:rfp_id>/submit'], type='http', auth='user', methods=['POST'],
                website=True)
    def rfp_submit(self, rfp_id, **kw):
        error_list = []
        success_list = []

        rfp = request.env['procurement_management.rfp'].sudo().browse(rfp_id)

        # Validate warranty period (cannot be negative)
        warranty_period = int(kw.get('warranty_period', 0))
        if warranty_period < 0:
            error_list.append("Warranty period cannot be negative.")

        # Validate expected delivery date (cannot be a past date)
        expected_delivery_date = kw.get('expected_delivery_date')
        if expected_delivery_date:
            expected_delivery_date = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
            if expected_delivery_date < datetime.today().date():
                error_list.append("Expected delivery date cannot be a past date.")
        else:
            error_list.append("Expected delivery date is required.")

        # Validate unit price and delivery charge for each product line
        for line in rfp.product_line_ids:
            unit_price = float(kw.get(f'order_line_unit_price_{line.id}', 0))
            delivery_charge = float(kw.get(f'order_line_delivery_charge_{line.id}', 0))

            if unit_price < 0:
                error_list.append(f"Unit price for product '{line.product_id.name}' cannot be negative.")
            if delivery_charge < 0:
                error_list.append(f"Delivery charge for product '{line.product_id.name}' cannot be negative.")

        # If there are errors, redirect back to the form page with error messages
        if error_list:
            return request.render('procurement_management.rfp_form_view_template', {
                'rfp': rfp,
                'error_list': error_list,
                'page_name':'rfp_id'
            })

        # If no errors, create the RFQ
        rfq_values = {
            'rfp_id': rfp.id,
            'partner_id': request.env.user.partner_id.id,
            'warranty_period': warranty_period,
            'expected_delivery_date': expected_delivery_date,
            'user_id': rfp.create_uid.id,
        }
        rfq = request.env['purchase.order'].sudo().create(rfq_values)
        success_list.append('RFQ submitted successfully.')

        # Create RFQ lines
        for line in rfp.product_line_ids:
            rfq_line = {
                'order_id': rfq.id,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_qty': line.quantity,
                'price_unit': float(kw.get(f'order_line_unit_price_{line.id}', 0)),
                'delivery_charge': float(kw.get(f'order_line_delivery_charge_{line.id}', 0)),
                'date_planned': expected_delivery_date,
            }
            request.env['purchase.order.line'].sudo().create(rfq_line)

        # Notify reviewer upon successful submission
        notify_reviewer_upon_quotation_submission(request, rfq)

        # Redirect to the submit page
        return request.render('procurement_management.rfq_submit_view_template', {
            'rfp': rfp,
            'success_list': success_list,
            'page_name': 'submit'
        })

    @http.route(['/procurement_management/my/rfqs', '/procurement_management/my/rfqs/page/<int:page>'], type='http', auth='user', website=True)
    def rfqs_list(self, page=1, sortby=None, search=None, search_in='all', groupby='none', **kw):
        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('RFQ Name'), 'order': 'name'},
            'state': {'label': _('State'), 'order': 'state'},
            'expected_delivery_date': {'label': _('Expected Delivery Date'), 'order': 'expected_delivery_date'},
        }

        # Searching options
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'name': {'label': _('RFQ Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]},
            'rfp_id': {'label': _('Linked RFP'), 'input': 'rfp_id', 'domain': [('rfp_id.rfp_id_seq', 'ilike', search)]},
        }

        # Apply search filters
        search_domain = search_list[search_in]['domain'] if search and search_in in search_list else []

        # Add condition to only include RFQs for the current user
        user = request.env.user
        search_domain.append(('partner_id', '=', user.partner_id.id))

        # Default sorting
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Grouping options
        if not groupby or groupby == 'none':
            groupby = 'state'
        groupby_list = {
            'none': {'label': _('None'), 'input': ''},
            'state': {'label': _('State'), 'input': 'state'},
            'expected_delivery_date': {'label': _('Expected Delivery Date'), 'input': 'expected_delivery_date'},
        }

        # Ensure group_by_rfq is always a dictionary
        group_by_rfq = groupby_list.get(groupby, {'input': None})

        # Pagination setup
        rfq_obj = request.env['purchase.order']
        rfq_count = rfq_obj.search_count(search_domain)
        items_per_page = 5  # Adjust as needed
        pager = portal_pager(
            url='/procurement_management/my/rfqs',
            total=rfq_count,
            page=page, step=items_per_page,
            scope=5,
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby}
        )

        # Fetch paginated records
        rfqs = rfq_obj.search(search_domain, limit=items_per_page, offset=pager['offset'], order=order)

        # Grouping logic
        if group_by_rfq['input']:  # Only group if valid input is provided
            rfq_group_list = [{group_by_rfq['input']: key, 'rfqs': list(group)}
                              for key, group in groupbyelem(rfqs, itemgetter(group_by_rfq['input']))]
        else:
            rfq_group_list = [{'rfqs': rfqs}]

        return request.render('procurement_management.rfq_list_view_template', {
            'group_rfqs': rfq_group_list,
            'page_name': 'my_rfq',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'default_url': '/procurement_management/my/rfqs',
            'groupby': groupby,
            'searchbar_groupby': groupby_list,
        })

    @http.route('/procurement_management/rfq/<int:rfq_id>', type='http', auth="user", website=True)
    def rfq_details(self, rfq_id):
        rfq = request.env['purchase.order'].sudo().browse(rfq_id)
        if not rfq.exists():
            return request.not_found()
        values = {
            'rfq': rfq,
            'page_name':'rfq_details'
        }
        return request.render('procurement_management.rfq_form_view_template', values)
