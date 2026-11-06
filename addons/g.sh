#!/bin/bash
# ---------------------------------------------------------------
# Genera el mòdul "matricula_estudis" (Odoo 19) i el puja al servidor.
#
# Ús (des de la carpeta addons, o des de qualsevol altra):
#     bash crear_matricula_estudis.sh
#
# - Si l'executes DINS del servidor, en ~/odoo/addons, només crea el mòdul.
# - Si l'executes al teu PC, crea el mòdul i el puja per ssh.
# ---------------------------------------------------------------
set -e

MOD="matricula_estudis"
SERVER="alumne@10.20.8.155"
REMOTE_ADDONS="~/odoo/addons"

echo ">> Creant l'estructura de $MOD ..."
mkdir -p "$MOD/models" "$MOD/views" "$MOD/security"

# ---------------- __init__.py ----------------
cat > "$MOD/__init__.py" << 'PYEOF'
from . import models
PYEOF

cat > "$MOD/models/__init__.py" << 'PYEOF'
from . import models
PYEOF

# ---------------- __manifest__.py ----------------
cat > "$MOD/__manifest__.py" << 'PYEOF'
# -*- coding: utf-8 -*-
{
    'name': "Matriculació d'estudis",
    'summary': "Gestió d'inscripcions d'alumnes en cursos amb regles de negoci",
    'author': "David",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
PYEOF

# ---------------- models/models.py ----------------
cat > "$MOD/models/models.py" << 'PYEOF'
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
PYEOF

# ---------------- security/ir.model.access.csv ----------------
cat > "$MOD/security/ir.model.access.csv" << 'CSVEOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_matricula_curs,matricula.curs user,model_matricula_curs,base.group_user,1,1,1,1
access_matricula_alumne,matricula.alumne user,model_matricula_alumne,base.group_user,1,1,1,1
access_matricula_inscripcio,matricula.inscripcio user,model_matricula_inscripcio,base.group_user,1,1,1,1
CSVEOF

# ---------------- views/views.xml ----------------
cat > "$MOD/views/views.xml" << 'XMLEOF'
<odoo>
    <!-- Inscripció: llista i formulari amb el domain sobre el camp computat -->
    <record id="matricula_inscripcio_view_list" model="ir.ui.view">
        <field name="name">matricula.inscripcio.list</field>
        <field name="model">matricula.inscripcio</field>
        <field name="arch" type="xml">
            <list>
                <field name="curs_id"/>
                <field name="alumne_id"/>
                <field name="data_inscripcio"/>
            </list>
        </field>
    </record>

    <record id="matricula_inscripcio_view_form" model="ir.ui.view">
        <field name="name">matricula.inscripcio.form</field>
        <field name="model">matricula.inscripcio</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <field name="curs_id"/>
                        <field name="alumne_id"
                               domain="[('id', 'in', alumne_elegible_ids)]"/>
                        <field name="data_inscripcio"/>
                        <field name="alumne_elegible_ids" invisible="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Accions -->
    <record id="matricula_curs_action" model="ir.actions.act_window">
        <field name="name">Cursos</field>
        <field name="res_model">matricula.curs</field>
        <field name="view_mode">list,form</field>
    </record>
    <record id="matricula_alumne_action" model="ir.actions.act_window">
        <field name="name">Alumnes</field>
        <field name="res_model">matricula.alumne</field>
        <field name="view_mode">list,form</field>
    </record>
    <record id="matricula_inscripcio_action" model="ir.actions.act_window">
        <field name="name">Inscripcions</field>
        <field name="res_model">matricula.inscripcio</field>
        <field name="view_mode">list,form</field>
    </record>

    <!-- Menús -->
    <menuitem id="matricula_menu_root" name="Matriculació" sequence="10"/>
    <menuitem id="matricula_menu_cursos" name="Cursos"
              parent="matricula_menu_root" action="matricula_curs_action"/>
    <menuitem id="matricula_menu_alumnes" name="Alumnes"
              parent="matricula_menu_root" action="matricula_alumne_action"/>
    <menuitem id="matricula_menu_inscripcions" name="Inscripcions"
              parent="matricula_menu_root" action="matricula_inscripcio_action"/>
</odoo>
XMLEOF

echo ">> Mòdul generat a: $(pwd)/$MOD"

# ---------------- Desplegament ----------------
if [ "$(pwd)" = "$HOME/odoo/addons" ]; then
    # Estem al servidor, dins d'addons
    chmod -R 777 "$MOD"
    echo ">> Permisos aplicats. Ja és a la carpeta correcta del servidor."
    read -r -p ">> Reiniciar Odoo ara? [s/N] " RESP
    if [ "$RESP" = "s" ] || [ "$RESP" = "S" ]; then
        (cd "$HOME/odoo" && docker compose restart odoo)
    fi
ele
    echo ">> Pujant el mòdul a $SERVER:$REMOTE_ADDONS (et demanarà la contrasenya) ..."
    tar czf - "$MOD" | ssh "$SERVER" \
        "tar xzf - -C $REMOTE_ADDONS && chmod -R 777 $REMOTE_ADDONS/$MOD"
    echo ">> Mòdul pujat."
    read -r -p ">> Reiniciar Odoo al servidor ara? [s/N] " RESP
    if [ "$RESP" = "s" ] || [ "$RESP" = "S" ]; then
        ssh "$SERVER" "cd ~/odoo && docker compose restart odoo"
    fi
fi

cat << 'FIN'
