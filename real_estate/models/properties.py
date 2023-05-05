from odoo import _,fields,models,api,exceptions
from datetime import timedelta,date,datetime
from odoo.exceptions import UserError ,ValidationError


class EstateProperty(models.Model):
    _name = 'estate.property'

    def action_cancel(self):
        if self.status_text == 'sold':
            raise UserError('A sold property cannot be canceled.')
        else:
            self.status_text = 'canceled'

    def action_sold(self):
        if self.status_text == 'canceled':
            raise UserError('A canceled property cannot be set as sold.')
        else:
            self.status_text = 'sold'

    @api.constrains('expected_price')
    def constrains_price(self):
        for rec in self:
            if rec.expected_price < 0:
                raise ValidationError(_(' The the unexpected Price must be strictly Positive'))


    # def action_cancel(self):
    #         if not self.status_text == 'canceled':
    #             raise UserError('Canceled properties cannot be sold')
    #         else:
    #             self.status_text = 'sold'

    # def action_cancel(self):
    #     for record in self:
    #         if not record.sold:
    #             record.canceled = True
    #status_text
    # def action_sold(self):
    #     for record in self:
    #         if not record.canceled:
    #             record.sold = True
    @api.model
    def _get_default_user(self):
        return self.env.context.get('user_id', self.env.user.id)
    @api.model
    def _get_default_buyer(self):
        return self.env.context.get('buyer_id', self.env.user.id)

    @api.depends('living_area', 'garden_area')
    def compute_total_area(self):
        for rec in self:
            rec.total_area = 0
            if rec.living_area and rec.garden_area:
                rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids.price')
    def compute_price(self):
        for rec in self:
            rec.best_offer = 0
            for emp in rec.offer_ids:
                if emp.price > rec.best_offer:
                    rec.best_offer = emp.price

    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.orientation = 'north'
        else:
            self.garden_area = False
            self.orientation = False
    #
    # def set_employee_status(self, vals):
    #     for rec in self:
    #         for emp in rec.offer_ids:
    #             if vals.get(emp.status) == 'accepted':
    #                 vals[rec.status] = 'offer_accepted'
    #             return vals
    #
    # def write(self, vals):
    #     vals = self.set_employee_status(vals)
    #     res = super(EstateProperty, self).write(vals)
    #     return res

    name = fields.Char(string='Name')
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    post_code = fields.Integer(string='Postcode')
    available_from = fields.Date(string='Available From')
    expected_price = fields.Float(string='Expected Price')
    best_offer = fields.Float(string='Best Offer' ,compute='compute_price')
    selling_price = fields.Float(string='Selling Price')
    status = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted','Offer Accepted'),
        ('sold','Sold')],
        'Status', default='new')
    description = fields.Text(string='Description')
    bedrooms = fields.Integer(string='Bedrooms')
    living_area = fields.Integer(string='Living Area(sqm)')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    total_area = fields.Integer(string='Total Area', compute='compute_total_area')
    color = fields.Integer('Color Index', default=0)
    offer_ids = fields.One2many('estate.property.offer','property_id', string='Offer')
    user_id = fields.Many2one('res.users', string="Sales Person", default=_get_default_user)
    buyer_id = fields.Many2one('res.partner', string="Buyer", default=_get_default_buyer)
    orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
                                   string='Garden Orientation')
    status_text = fields.Selection([('new','New'),
                                    ('sold','Sold'),
                                    ('canceled','Canceled')],
                                   string='Status', default='new')
    # sold = fields.Boolean(string='Sold', default=False)
    # canceled = fields.Boolean(string='Canceled', default=False)

    def accepted_button(self):
        for rec in self:
            for emp in rec.offer_ids:
                emp.status = 'accepted'
                if emp.status == 'accepted':
                    self.write({
                            'selling_price': emp.price,
                            'buyer_id' : emp.partner_id.id,
                        })

    def refused_button(self):
        for rec in self:
            for emp in rec.offer_ids:
                emp.status = 'refused'
                if emp.status == 'refused':
                    self.write({
                            'selling_price': 0 ,
                            'buyer_id' :  [('buyer_id','=','')]
                        })

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < 0.9 * record.expected_price:
                raise ValidationError(_("Selling price cannot be lower than 90% of the expected price."))


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'

    property_id = fields.Many2one('estate.property',string='Property')
    status = fields.Selection([('refused','Refused'),
                               ('accepted','Accepted')],
                              'Status')
    validity = fields.Integer(string='Validity(days)')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one('res.partner')
    deadline = fields.Date(string='Deadline' ,inverse='_set_validity_date' ,compute='_compute_validity_date')
    # validity_date = fields.Date(string='Validity Date', compute='_compute_validity_date', inverse='_set_validity_date', store=True)

    def _compute_validity_date(self):
        for offer in self:
            offer.deadline = fields.Date.today() + timedelta(days=offer.validity)

    # Inverse method
    def _set_validity_date(self):
        for offer in self:
            offer.validity = (offer.deadline - fields.Date.today()).days

    # Onchange method
    @api.onchange('validity')
    def onchange_validity_days(self):
        self.deadline = fields.Date.today() + timedelta(days=self.validity)

    # def refused_button(self):
    #     for rec in self:
    #         rec.status = 'refused'


    # def accept_offer(self):
    #     for offer in self:
    #         property = offer.property_id
    #         property.write({
    #             'selling_price': offer.price
    #         })


