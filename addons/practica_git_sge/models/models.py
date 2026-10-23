from odoo import models, fields


class ModelPractica(models.Model):
    _name = 'practica_git_sge.practica'
    _description = 'Model de prova per a la pràctica de Git'

    name = fields.Char(string="Nom de prova", required=True)
