from odoo import models, fields

class HmsPatientLog(models.Model):
    _name = 'hms.patient.log'
    _rec_name = 'patient_id'
    _description = 'Patient Log'

    patient_id = fields.Many2one(comodel_name='hms.patient')
    created_by = fields.Many2one(comodel_name='res.users')
    date = fields.Datetime()
    description = fields.Text()
