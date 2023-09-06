from odoo import models


class EstateProperty(models.Model):


    _inherit = "estate.property"


    def sold(self):
        res = super().sold()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_line_ids': [],
        }
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)

        return res