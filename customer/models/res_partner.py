from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    related_patient_id = fields.Many2one(
        comodel_name='hms.patient',
        string='Related Patient',
        help='Link this customer to a hospital patient'
    )
    vat = fields.Char(required=True, string='Tax ID', help="Tax Identification Number")

    @api.constrains('email', 'related_patient_id')
    def _check_email_unique_between_models(self):
        for record in self:
            if record.email and self.env['hms.patient'].search([('email', '=', record.email)]):
                raise ValidationError("This email is already used by a patient.")

    def unlink(self):
        for rec in self:
            if rec.related_patient_id:
                raise ValidationError("You cannot delete a customer linked to a patient.")
        return super().unlink()
