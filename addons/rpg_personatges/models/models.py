from odoo import models, fields


class Classe(models.Model):
    _name = 'rpg.classe'
    _description = 'Classe de personatge'

    name = fields.Char(string='Nom', required=True)


class Habilitat(models.Model):
    _name = 'rpg.habilitat'
    _description = 'Habilitat'

    name = fields.Char(string='Nom', required=True)
    nivell = fields.Integer(string='Nivell', default=1)


class Personatge(models.Model):
    _name = 'rpg.personatge'
    _description = 'Personatge'

    name = fields.Char(string='Nom', required=True)
    classe_id = fields.Many2one('rpg.classe', string='Classe')
    data_creacio = fields.Date(string='Data de creació')
    imatge = fields.Image(string='Imatge', max_width=512, max_height=512)
    habilitat_ids = fields.Many2many('rpg.habilitat', string='Habilitats')


class Avaluador(models.Model):
    _name = 'rpg.avaluador'
    _description = 'Registre de control per a l\'avaluació automàtica'
    _rec_name = 'requisit'

    nom_model = fields.Char(string='Nom del model')
    ext_id = fields.Char(string='ID extern complet')
    requisit = fields.Selection([
        ('img', 'Imatge'),
        ('ref', 'Referència'),
        ('dat', 'Data Calculada'),
        ('m2m', 'Relació Many2many'),
    ], string='Requisit')
