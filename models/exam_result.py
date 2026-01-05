from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolExamResult(models.Model):
    _name = "school.exam.result"
    _description = "Exam Result"
    _rec_name = "student_id"

    exam_id = fields.Many2one("school.exam", required=True)
    student_id = fields.Many2one("school.student", required=True)
    marks_obtained = fields.Integer(required=True)
    grade = fields.Char(compute="_compute_grade", store=True)

    class_id = fields.Many2one(
        related="exam_id.class_id", store=True, readonly=True
    )

    @api.depends("marks_obtained", "exam_id.max_marks")
    def _compute_grade(self):
        for rec in self:
            if not rec.exam_id.max_marks:
                rec.grade = ""
                continue
            pct = (rec.marks_obtained / rec.exam_id.max_marks) * 100
            if pct >= 85:
                rec.grade = "A"
            elif pct >= 70:
                rec.grade = "B"
            elif pct >= 50:
                rec.grade = "C"
            else:
                rec.grade = "F"

    @api.constrains("marks_obtained")
    def _check_marks(self):
        for rec in self:
            if rec.marks_obtained < 0:
                raise ValidationError("Marks cannot be negative.")
            if rec.exam_id and rec.marks_obtained > rec.exam_id.max_marks:
                raise ValidationError("Marks cannot exceed Max Marks.")
