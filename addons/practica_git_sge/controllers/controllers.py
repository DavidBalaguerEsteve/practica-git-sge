# from odoo import http


# class PracticaGitSge(http.Controller):
#     @http.route('/practica_git_sge/practica_git_sge', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/practica_git_sge/practica_git_sge/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('practica_git_sge.listing', {
#             'root': '/practica_git_sge/practica_git_sge',
#             'objects': http.request.env['practica_git_sge.practica_git_sge'].search([]),
#         })

#     @http.route('/practica_git_sge/practica_git_sge/objects/<model("practica_git_sge.practica_git_sge"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('practica_git_sge.object', {
#             'object': obj
#         })

