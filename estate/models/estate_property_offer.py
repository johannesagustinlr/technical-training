from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffer(models.Model):

    _name = "estate.property.offer"
    _description = "Estate property offer"
    _order = "price desc"
    
    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "The price must be strictly positive"),
    ]

    price = fields.Float(required=True)
    status = fields.Selection([("a", "Accepted"),("r", "Refused")],copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", readonly=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_deadline",inverse="_inverse_deadline")

    @api.depends("create_date", "validity")
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                date = record.create_date.date()
                record.date_deadline = date + relativedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today()

    def _inverse_deadline(self):
        for record in self:
            if record.create_date:
                date = record.create_date.date()
                record.validity = (record.date_deadline - date).days
            else:
                record.date_deadline = fields.Date.today()

   
    def accept(self):
        if "a" in self.mapped("property_id.offer_ids.status"):
            raise UserError("An offer as already been accepted.")
        self.write({"state": "a",} )
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer_id": self.partner_id.id,
            })

    def refuse(self):
       self.write({"state": "r",} )

