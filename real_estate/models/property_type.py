from odoo import fields,models


class PropertyType(models.Model):
    _name = 'estate.property.type'

    name = fields.Char(string='Name')
    property_ids = fields.One2many('estate.related','property_type_id', string='Properties')

    _sql_constraints = [
        ('name', 'unique (name)', 'The Property Type must be unique !')
    ]



class PropertyRelated(models.Model):
    _name = 'estate.related'

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    property_id = fields.Many2one('estate.property',string='Property', domain="[('property_type_id','=', property_type_id)]")
    expected_price = fields.Float(string='Expected Price', related='property_id.expected_price')
    status_text = fields.Selection(string='Status', related= 'property_id.status_text')

