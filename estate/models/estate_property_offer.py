from odoo import models, fields, api
from datetime import timedelta, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offers Model"
    _sql_constraints = [('check_offer_price_positive', 'CHECK(price > 0)','The offer price must be strictly positive')]

    price = fields.Float(string="Price")
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], copy=False, string="Status")
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(string="Deadline",  compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends('validity','date_deadline')
    def _compute_date_deadline(self):
        for day in self:
            day.date_deadline = date.today() + timedelta(days=day.validity)

    def _inverse_date_deadline(self):
        for day in self:
            day.validity = (day.date_deadline - day.create_date.date()).days if day.create_date else (day.date_deadline - date.today()).days

    def action_accept(self):
        for record in self:
            record.status = ('accepted')
            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id
        return True

    def action_refuse(self):
        for record in self:
            record.status = ('refused')
            record.property_id.selling_price = ''
        return True

    @api.constrains('price')
    def _constrains_selling_price(self):
        for record in self:
            ept_price = record.property_id.expected_price
            if float_compare(ept_price * 0.9, record.price,2):
                raise ValidationError('The selling price must be at least 90\% of the expected price! You must reduce the expected price if you want to accept this order')
        