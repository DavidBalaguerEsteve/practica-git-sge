# -*- coding: utf-8 -*-
{
    'name': "RPG personatges",
    'summary': "Personatges de rol amb dades de demostració carregades des d'XML",
    'author': "David",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
