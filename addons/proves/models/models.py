from odoo import models, fields


class HolaMon(models.Model):
    _name = 'proves.hola_mon'
    _description = 'Hola Món'

    name = fields.Char(string='Nom', required=True)
    enter = fields.Integer(string='Enter', required=True)
    descripcio = fields.Text(string='Descripció')
    decimal = fields.Float(string='Decimal', default=1.5)
    actiu = fields.Boolean(string='Actiu', default=True)
    data_alta = fields.Date(string='Data', default=fields.Date.today)
    data_hora = fields.Datetime(string='Data i hora')
    contingut = fields.Html(string='Contingut HTML')
    fitxer = fields.Binary(string='Fitxer')
    imatge = fields.Image(string='Imatge', max_width=512, max_height=512)
    estat = fields.Selection(
        [('esborrany', 'Esborrany'),
         ('actiu', 'Actiu'),
         ('tancat', 'Tancat')],
        string='Estat', default='esborrany')
