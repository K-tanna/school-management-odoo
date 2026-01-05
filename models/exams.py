from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolExam(models.Model):
    _name = "school.exam"
    _description = "School Exam"
    _order = "exam_date desc"

    name = fields.Char(required=True)
    class_id = fields.Many2one("school.class", required=True)
    subject = fields.Char(required=True)
    exam_date = fields.Date(required=True)
    max_marks = fields.Integer(required=True)


    @api.constrains("max_marks")
    def _check_max_marks(self):
        for rec in self:
            if rec.max_marks <= 0:
                raise ValidationError("Max marks must be greater than zero.")

    result_ids = fields.One2many(
        "school.exam.result", "exam_id", string="Results"
    )

    result_count = fields.Integer(
        compute="_compute_result_count", string="Results"
    )

    @api.depends("result_ids")
    def _compute_result_count(self):
        for rec in self:
            rec.result_count = len(rec.result_ids)

    def action_view_results(self):
        self.ensure_one()
        return {
            "name": "Results",
            "type": "ir.actions.act_window",
            "res_model": "school.exam.result",
            "view_mode": "list,form",
            "domain": [("exam_id", "=", self.id)],
            "context": {"default_exam_id": self.id},
        }
        

