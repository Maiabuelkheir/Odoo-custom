from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date
import re

class HmsPatient(models.Model):
    _name = 'hms.patient' 
    _rec_name = 'first_name'
    _description = 'Patient Details'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    birth_date = fields.Date()
    email = fields.Char(required=True) 
    history = fields.Html()
    Cr_ratio = fields.Float()
    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ])
    pcr = fields.Boolean()  
    image = fields.Binary()  
    address = fields.Text()  
    department_id = fields.Many2one(comodel_name='hms.department', domain="[('is_opened', '=', True)]")
    log_ids = fields.One2many(comodel_name='hms.patient.log', inverse_name='patient_id')
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], string="Condition State")
    doctor_ids = fields.Many2many('hms.doctor', string="Doctors")

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                age = today.year - record.birth_date.year
                if (today.month, today.day) < (record.birth_date.month, record.birth_date.day):
                    age -= 1
                record.age = age
            else:
                record.age = 0

    def good_patient(self):
        for rec in self:
            rec.state = 'good'

    def fair_patient(self):
        for rec in self:
            rec.state = 'fair'

    def serious_patient(self):
        for rec in self:
            rec.state = 'serious'

    def validate_email(self, email):
        """Validate email format using regex"""
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, email):
            raise UserError("Invalid email address.")

    @api.model
    def create(self, vals):
        if vals.get('first_name'):
            vals['first_name'] = vals['first_name'].strip().title()
        if vals.get('email'):
            self.validate_email(vals['email'])
        if self.search([('email', '=', vals.get('email'))]):
            raise UserError("This email address is already in use by another patient.")
        return super().create(vals)

    def write(self, vals):
        if vals.get('first_name'):
            vals['first_name'] = vals['first_name'].strip().title()
        if 'email' in vals:
            self.validate_email(vals['email'])
            if self.search([('email', '=', vals['email']), ('id', '!=', self.id)]):
                raise UserError("This email address is already in use by another patient.")
        if 'state' in vals:
            for rec in self:
                if rec.state != vals['state']:
                    self.env['hms.patient.log'].create({
                        'patient_id': rec.id,
                        'description': f"State changed from {rec.state} to {vals['state']}"
                    })
        return super().write(vals)
    
    @api.constrains('pcr', 'Cr_ratio')
    def _check_cr_ratio_required(self):
        for record in self:
            if record.pcr and not record.Cr_ratio:
                raise UserError("CR Ratio is required when PCR is checked.")
    @api.onchange('age')
    def _onchange_age_check_pcr(self):
        for rec in self:
            if rec.age and rec.age < 30 and not rec.pcr:
                rec.pcr = True
                return {
                    'warning': {
                        'title': "PCR Checked Automatically",
                        'message': "PCR has been checked automatically because age is less than 30.",
                    }
                }

    def unlink(self):
        for rec in self:
            if rec.state == 'serious':
                raise UserError("You cannot delete a patient with a serious condition.")
        return super().unlink()



  