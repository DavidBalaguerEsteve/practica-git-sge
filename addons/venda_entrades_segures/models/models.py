from datetime import timedelta

from markupsafe import Markup

from odoo import models, fields, api


class Esdeveniment(models.Model):
    _name = 'venda_entrades_segures.esdeveniment'
    _description = 'Esdeveniment'

    name = fields.Char(string='Nom', required=True)
    preu_base = fields.Float(string='Preu base')
    data_inici = fields.Datetime(string="Data d'inici")


class Etiqueta(models.Model):
    _name = 'venda_entrades_segures.etiqueta'
    _description = 'Etiqueta'

    name = fields.Char(string='Nom', required=True)


class Tiquet(models.Model):
    _name = 'venda_entrades_segures.tiquet'
    _description = 'Tiquet'
    
    name = fields.Char(string='Nom')

    def _get_default_tags(self):
        nominal = self.env.ref('venda_entrades_segures.etiqueta_nominal')
        no_reemb = self.env.ref('venda_entrades_segures.etiqueta_no_reemborsable')
        return [(6, 0, [nominal.id, no_reemb.id])]

    comprador_id = fields.Many2one('res.partner', string='Comprador', required=True)
    esdeveniment_id = fields.Many2one(
        'venda_entrades_segures.esdeveniment', string='Esdeveniment', required=True)

    preu_final = fields.Float(
        string='Preu final', compute='_compute_preu_final', store=True)
    codi_seguretat = fields.Char(
        string='Codi de seguretat', compute='_compute_codi_seguretat')
    data_limit_acces = fields.Datetime(
        string="Data límit d'accés", compute='_compute_data_limit_acces')
    foto_comprador = fields.Image(
        string='Foto del comprador', compute='_compute_foto_comprador')
    clausules_legals = fields.Html(
        string='Clàusules legals', compute='_compute_clausules_legals')
    etiquetes_ids = fields.Many2many(
        'venda_entrades_segures.etiqueta',
        'venda_tiquet_etiqueta_rel', 'tiquet_id', 'etiqueta_id',
        string='Etiquetes', default=_get_default_tags)
    entrades_relacionades_ids = fields.Many2many(
        'venda_entrades_segures.tiquet',
        'venda_tiquet_relacionat_rel', 'tiquet_id', 'relacionat_id',
        string='Entrades relacionades', compute='_compute_entrades_relacionades')

    @api.depends('esdeveniment_id.preu_base')
    def _compute_preu_final(self):
        for record in self:
            record.preu_final = record.esdeveniment_id.preu_base * 1.10

    @api.depends('comprador_id.name', 'esdeveniment_id')
    def _compute_codi_seguretat(self):
        for record in self:
            nom = record.comprador_id.name or ''
            record.codi_seguretat = f"{nom}-{record.esdeveniment_id.id or 0}"

    @api.depends('esdeveniment_id.data_inici')
    def _compute_data_limit_acces(self):
        for record in self:
            inici = record.esdeveniment_id.data_inici
            record.data_limit_acces = inici - timedelta(hours=2) if inici else False

    @api.depends('comprador_id.image_1920')
    def _compute_foto_comprador(self):
        for record in self:
            record.foto_comprador = record.comprador_id.image_1920

    @api.depends('comprador_id.name')
    def _compute_clausules_legals(self):
        for record in self:
            record.clausules_legals = Markup(
                "<p>Aquesta entrada és <b>nominal</b> i pertany a <b>%s</b>.</p>"
                "<p>Queda prohibida la revenda o cessió a tercers.</p>"
            ) % (record.comprador_id.name or '')

    @api.depends('esdeveniment_id', 'comprador_id')
    def _compute_entrades_relacionades(self):
        for record in self:
            if record.esdeveniment_id and record.comprador_id:
                domain = [
                    ('esdeveniment_id', '=', record.esdeveniment_id.id),
                    ('comprador_id', '=', record.comprador_id.id),
                    ('id', '!=', record._origin.id),
                ]
                record.entrades_relacionades_ids = self.search(domain)
            else:
                record.entrades_relacionades_ids = self.browse()
