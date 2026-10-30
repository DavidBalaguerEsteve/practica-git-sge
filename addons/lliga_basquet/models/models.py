from odoo import models, fields


class Pavello(models.Model):
    _name = 'basquet.pavello'
    _description = 'Pavelló'

    name = fields.Char(string='Nom', required=True)
    ciutat = fields.Char(string='Ciutat')


class Equip(models.Model):
    _name = 'basquet.equip'
    _description = 'Equip'

    name = fields.Char(string='Nom', required=True)
    ciutat = fields.Char(string='Ciutat')
    jugador_ids = fields.One2many('basquet.jugador', 'equip_id', string='Jugadors')
    estadi_id = fields.Many2one(
        'basquet.pavello', string='Estadi principal',
        domain="[('ciutat', '=', ciutat)]")
    equips_agermanats_ids = fields.Many2many(
        'basquet.equip',
        'basquet_equip_agermanats_rel', 'equip_id', 'agermanat_id',
        string='Equips agermanats')
    equips_rivals_ids = fields.Many2many(
        'basquet.equip',
        'basquet_equip_rivals_rel', 'equip_id', 'rival_id',
        string='Equips rivals')


class Jugador(models.Model):
    _name = 'basquet.jugador'
    _description = 'Jugador'

    name = fields.Char(string='Nom', required=True)
    equip_id = fields.Many2one(
        'basquet.equip', string='Equip',
        domain="[('estadi_id', '!=', False)]")
    estadi_nom = fields.Char(
        string='Estadi', related='equip_id.estadi_id.name')
    es_capita = fields.Boolean(string='És capità')
