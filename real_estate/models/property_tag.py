from odoo import _,fields,models,api
from odoo.exceptions import UserError ,ValidationError


class PropertyTag(models.Model):
    _name = 'estate.property.tag'

    name = fields.Char(string='Name')
    color = fields.Integer('Color Index', default=0)



    _sql_constraints = [
        ('name', 'unique (name)', 'The Property Tag must be unique !')
    ]
