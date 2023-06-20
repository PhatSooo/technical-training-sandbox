from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag Model"
    _sql_constraints = [('check_tag_name_unique', 'UNIQUE(name)', 'The tag name must be unique')]

    name = fields.Char(required=True)
