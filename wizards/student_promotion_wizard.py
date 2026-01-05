from odoo import models, fields

class StudentPromotionWizard(models.TransientModel):
    _name = 'student.promotion.wizard'
    _description = 'Student Promotion Wizard'

    student_id = fields.Many2one(
        'school.student',
        string="Student",
        readonly=True
    )

    current_class_id = fields.Many2one(
        'school.class',
        string="Current Class",
        readonly=True
    )

    new_class_id = fields.Many2one(
        'school.class',
        string="New Class",
        required=True
    )

    def action_promote_student(self):
        self.student_id.write({
            'class_id': self.new_class_id.id
        })
