# -*- coding: utf-8 -*-
from odoo import api, http, modules
from odoo.http import request, Response

class ProcurementManagement(http.Controller):
    @http.route('/procurement_management/procurement_management', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/procurement_management/procurement_management/objects', auth='public')
    def list(self, **kw):
        return http.request.render('procurement_management.listing', {
            'root': '/procurement_management/procurement_management',
            'objects': http.request.env['procurement_management.procurement_management'].search([]),
        })

    @http.route('/procurement_management/procurement_management/objects/<model("procurement_management.procurement_management"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('procurement_management.object', {
            'object': obj
        })

    @http.route('/procurement_management/sign-up', auth='public',website=True)
    def sign_up(self, **kw):
        return request.render('procurement_management.sign_up_template',{})