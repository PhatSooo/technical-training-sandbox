from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property Model"

    estate_type_id = fields.Many2one("estate.property.type", string="Property Type")
    name = fields.Char(required=True, default="Unknown", string="Title")
    last_seen = fields.Datetime("Last Seen", default=lambda self: fields.Datetime.now())
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        copy=False,
        default=lambda self: datetime.today() + relativedelta(months=+3),
        string="Available From",
    )
    expected_price = fields.Float(required=True, string="Expected Price")
    selling_price = fields.Float(readonly=True, copy=False, string="Selling Price")
    bedrooms = fields.Integer(default=2, string="Bedrooms")
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        string="Garden Orientation",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("receive", "Offer Received"),
            ("accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default=("new"),
        string="Status",
    )
    active = fields.Boolean(default=False)
    salesman = fields.Many2one(
        "res.users",
        string="Salesperson",
        index=True,
        default=lambda self: self.env.user,
    )
    buyer = fields.Many2one(
        "res.partner",
        string="Buyer",
        index=True,
        default=lambda self: self._uid,
    )

    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Estate")

    total_area = fields.Integer(compute='_compute_area', string="Total Area (sqm)")
    best_price = fields.Float(compute='_compute_best_price', string="Best Offer")

    @api.depends('living_area','garden_area')
    def _compute_area(self):
        for area in self:
            area.total_area = area.living_area + area.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        self.best_price = max(self.offer_ids.mapped('price'))

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = ('north')
            return {
        'warning': {'title': "Warning", 'message': "What is this?", 'type': 'notification'},}
        else:
            self.garden_area = ''
            self.garden_orientation = ''

    def action_sold(self):
        for record in self:
            if record.state == ('canceled'):
                raise UserError('Canceled property can not be sold')
            else:
                record.state = ('sold')
        return True

    def action_cancel(self):
        for record in self:
            if record.state == ('sold'):
                raise UserError('Sold property can not be canceled')
            else: 
                record.state = ('canceled')
        return True