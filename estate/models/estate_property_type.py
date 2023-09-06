from odoo import fields, models, api

class EstatePropertyType(models.Model):

    _name = "estate.property.type"
    _description = "Estate property type"
    _order = "name"
    _sql_constraints = [('unique_name', 'unique(name)', 'A property type name must be unique')]
    
    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id",)
    sequence = fields.Integer(default=10)