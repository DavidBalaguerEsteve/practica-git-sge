from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Curs(models.Model):
    _name = 'matricula.curs'
    _description = 'Curs'

    name = fields.Char(string='Nom', required=True)
    edat_minima = fields.Integer(string='Edat mínima', default=0)
    capacitat_maxima = fields.Integer(string='Capacitat màxima', default=10)
    data_inici = fields.Date(string="Data d'inici")
    data_fi = fields.Date(string='Data de fi')
    inscripcio_ids = fields.One2many(
        'matricula.inscripcio', 'curs_id', string='Inscripcions')

    # Restricció SQL: la capacitat ha de ser superior a zero.
    # (En Odoo 19 _sql_constraints està deprecat: es declara amb models.Constraint)
    _capacitat_positiva = models.Constraint(
        'CHECK (capacitat_maxima > 0)',
        'La capacitat màxima ha de ser superior a zero.')

    # Restricció Python: dates coherents.
    @api.constrains('data_inici', 'data_fi')
    def _check_dates(self):
        for record in self:
            if record.data_inici and record.data_fi \
                    and record.data_fi < record.data_inici:
                raise ValidationError(
                    "La data de fi no pot ser anterior a la data d'inici.")


class Alumne(models.Model):
    _name = 'matricula.alumne'
    _description = 'Alumne'

    name = fields.Char(string='Nom', required=True)
    nif = fields.Char(string='NIF', required=True)
    edat = fields.Integer(string='Edat', default=18)

    # Restriccions SQL: NIF únic i edat positiva.
    _nif_unic = models.Constraint(
        'UNIQUE (nif)',
        'El NIF ha de ser únic: ja existeix un alumne amb aquest NIF.')
    _edat_positiva = models.Constraint(
        'CHECK (edat > 0)',
        "L'edat de l'alumne ha de ser un número positiu.")


class Inscripcio(models.Model):
    _name = 'matricula.inscripcio'
    _description = 'Inscripció'
    _rec_name = 'alumne_id'

    # El domain també es declara en Python perquè fields_get el retorne.
    alumne_id = fields.Many2one(
        'matricula.alumne', string='Alumne', required=True,
        domain="[('id', 'in', alumne_elegible_ids)]")
    curs_id = fields.Many2one(
        'matricula.curs', string='Curs', required=True, ondelete='cascade')
    data_inscripcio = fields.Date(
        string="Data d'inscripció", default=fields.Date.context_today)

    # Camp computat (no s'emmagatzema) amb els alumnes que es poden matricular.
    alumne_elegible_ids = fields.Many2many(
        'matricula.alumne',
        'matricula_inscripcio_elegible_rel', 'inscripcio_id', 'alumne_id',
        string='Alumnes elegibles',
        compute='_compute_alumne_elegible_ids', store=False)

    @api.depends('curs_id', 'curs_id.edat_minima', 'curs_id.inscripcio_ids.alumne_id')
    def _compute_alumne_elegible_ids(self):
        Alumne = self.env['matricula.alumne']
        for record in self:
            if not record.curs_id:
                record.alumne_elegible_ids = Alumne.browse()
                continue
            matriculats = self.search([
                ('curs_id', '=', record.curs_id.id),
                ('id', '!=', record._origin.id),
            ]).mapped('alumne_id')
            record.alumne_elegible_ids = Alumne.search([
                ('edat', '>=', record.curs_id.edat_minima),
                ('id', 'not in', matriculats.ids),
            ])

    # Restricció: data d'inscripció dins del rang del curs.
    @api.constrains('data_inscripcio', 'curs_id')
    def _check_data_inscripcio(self):
        for record in self:
            data = record.data_inscripcio
            curs = record.curs_id
            if not data:
                continue
            if curs.data_inici and data < curs.data_inici:
                raise ValidationError(
                    "La data d'inscripció és anterior a l'inici del curs.")
            if curs.data_fi and data > curs.data_fi:
                raise ValidationError(
                    "La data d'inscripció és posterior al final del curs.")

    # Restricció: edat mínima del curs.
    @api.constrains('alumne_id', 'curs_id')
    def _check_edat_minima(self):
        for record in self:
            if record.alumne_id.edat < record.curs_id.edat_minima:
                raise ValidationError(
                    "L'alumne %s no té l'edat mínima (%s anys) del curs %s." % (
                        record.alumne_id.name,
                        record.curs_id.edat_minima,
                        record.curs_id.name))

    # Restricció: control de places.
    @api.constrains('curs_id')
    def _check_places(self):
        for record in self:
            total = self.search_count([('curs_id', '=', record.curs_id.id)])
            if total > record.curs_id.capacitat_maxima:
                raise ValidationError(
                    "El curs %s ja ha arribat a la capacitat màxima (%s)." % (
                        record.curs_id.name, record.curs_id.capacitat_maxima))
