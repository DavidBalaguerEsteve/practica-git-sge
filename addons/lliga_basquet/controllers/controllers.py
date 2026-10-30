# from odoo import http


# class LligaBasquet(http.Controller):
#     @http.route('/lliga_basquet/lliga_basquet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lliga_basquet/lliga_basquet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('lliga_basquet.listing', {
#             'root': '/lliga_basquet/lliga_basquet',
#             'objects': http.request.env['lliga_basquet.lliga_basquet'].search([]),
#         })

#     @http.route('/lliga_basquet/lliga_basquet/objects/<model("lliga_basquet.lliga_basquet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lliga_basquet.object', {
#             'object': obj
#         })

