from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class EstateProperty(models.Model):

    _name = "estate.property"
    _description = "Estate property model"
    _order = "id desc"

    _sql_constraints = [
        ("check_expected_price", "CHECK (expected_price > 1)", "The expected price must be strictly positive"),
        ("check_selling_price", "CHECK (selling_price >= 0)", "The offer price must be positive"),
    ]
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Datetime.add(fields.Datetime.now(),months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly="True")
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[("north", "North"),("south", "South"),("east","East"),("west", "West")]
    )
    active=fields.Boolean(default=True)
    state = fields.Selection(
        required=True,
        copy=False,
        default="new",
        selection=[("new", "New"),("offer_received", "Offer Received"),("offer_accepted","Offer Accepted"),("sold", "Sold"),("canceled", "Canceled")]
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", readonly=True, copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(compute="_compute_total")
    best_price = fields.Float(compute = "_compute_price")
    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("cannot sold.")
        return self.write({"state": "sold"})

    def cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("cannot canceled.")
        return self.write({"state": "canceled"})
    

    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for prop in self:
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )
    
    def unlink(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled can be deleted.")
        return super().unlink()