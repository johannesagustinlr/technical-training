from . import estate_property

from odoo import models


class EstateProperty(models.Model):


    _inherit = "estate.property"


    def action_sold(self):
        res = super().sold()


        return res
