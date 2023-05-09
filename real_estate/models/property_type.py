from odoo import fields,models,api


class PropertyType(models.Model):
    _name = 'estate.property.type'

    name = fields.Char(string='Name')
    property_ids = fields.One2many('estate.related','property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string='Offers'
    )
    offer_count = fields.Integer(
        compute='_compute_offer_count'
    )

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)

    _sql_constraints = [
        ('name', 'unique (name)', 'The Property Type must be unique !')
    ]

    # def property_button(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Offer',
    #         'view_mode': 'list,form',
    #         'res_model': 'estate.property.offer',
    #         'domain': "[('property_type_id','in', )]" ,
    #         'target': "current"
    #     }

class PropertyRelated(models.Model):
    _name = 'estate.related'

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    property_id = fields.Many2one('estate.property',string='Property', domain="[('property_type_id','=', property_type_id)]")
    expected_price = fields.Float(string='Expected Price', related='property_id.expected_price')
    status_text = fields.Selection(string='Status', related= 'property_id.status_text')



