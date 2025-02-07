from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class MyRFQPortal(CustomerPortal):
    @http.route(['/procurement_management/rfps', '/procurement_management/rfps/page/<int:page>'], type='http', auth='user', website=True)
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

        search_domain = search_list[search_in]['domain'] if search and search_in in search_list else []

        # Default sorting
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not groupby or groupby == 'none':
            groupby = 'status'
        # Grouping options
        groupby_list = {
            'none': {'label': _('None'), 'input': ''},  # Added this line
            'status': {'label': _('Status'), 'input': 'status'},
            'required_date': {'label': _('Required Date'), 'input': 'required_date'},
        }

        # Ensure group_by_rfp is always a dictionary
        group_by_rfp = groupby_list.get(groupby, {'input': None})

        # Pagination setup
        rfp_obj = request.env['procurement_management.rfp']
        rfp_count = rfp_obj.search_count(search_domain)
        items_per_page = 5  # Adjust as needed
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

    @http.route('/procurement_management/rfp/<int:rfp_id>', auth='public', methods=['POST', 'GET'], website=True)
    def rfp_details(self,rfp_id,**kw):
        rfp=request.env['procurement_management.rfp'].browse(rfp_id)
        return request.render('procurement_management.rfp_form_view_template',{'rfp':rfp})



 