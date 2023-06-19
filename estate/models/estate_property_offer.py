from odoo import models, fields, api
from datetime import timedelta, date


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offers Model"

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
