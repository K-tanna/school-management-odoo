from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import date
import re

class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "School Student"

    name = fields.Char(string="Student Name", required=True)
    roll_no = fields.Integer(string="Student RollNo")
    dob = fields.Date(string="Date Of Birth")
    city = fields.Char(string="City")
    address = fields.Text(string="Address")

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")

    addmission = fields.Date(string="Admission Date")
    age = fields.Integer(string="Age",comput="_compute_age",store=True)
    height = fields.Float(string="Height (cm)")

    teacher_ids = fields.Many2many("school.teacher", string="Teachers")
    class_id = fields.Many2one("school.class", string="Class")

    image_1920 = fields.Image(string="Photo")
    notes = fields.Html(string="Notes")
    #fees=fields.Monetary(string="fees")
    fees_id = fields.One2many("school.fees","student_id",string="Fees")
    fees_count=fields.Integer(compute="_compute_fees_count")

    @api.depends('fees_id')
    def _compute_fees_count(self):
        for rec in self:
            rec.fees_count = len(rec.fees_id)

    @api.depends('dob')
    def _compute_age(self):
        today=date.today()
        for rec in self:
            if rec.dob:
                rec.age=today.year-dob.year-(today.month-dob.month)<(rec.dob.month,rec.dob.day)
            

    def action_view_class(self):
        self.ensure_one()
        if not self.class_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Class',
            'res_model': 'school.class',
            'view_mode': 'form',
            'res_id': self.class_id.id,
        }

    def action_view_fees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fees',
            'res_model': 'school.fees',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    '''def action_student_graph(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students Analysis',
            'res_model': 'school.student',
            'view_mode': 'graph',
            'domain': [('class_id', '=', self.id)],
        }'''


    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age<=0:
                raise ValidationError("Age Can't be Zero or Negative")

    @api.constrains('class_id')
    def _check_classid(self):
        for record in self:
            if not record.class_id:
                raise ValidationError("Student Must Assign the Class")

    @api.constrains('addmission')
    def _check_addmission(self):
        today=fields.Date.today()
        for rec in self:
            if rec.addmission and rec.addmission >today:
                raise ValidationError("Date Invalid")

    @api.onchange('class_id') #shows rollno automatically acc to class in UI
    # this method shows the roll no according the class's last no allocated
    def _onchange_class_for_rollno(self):
        if self.class_id:              #here self represents the unsaved record so need to write env
            students=self.env['school.student'].search_count([
                ('class_id','=',self.class_id.id)])
            self.roll_no=students+1

    @api.model #roll no will be stored in db acc to selected class
    def create(self, vals_list):
        for vals in vals_list:   # here self reprents the model so no need to write the env
            if vals.get('class_id'):
                last_student = self.search(
                    [('class_id', '=', vals['class_id'])],
                    order='roll_no desc',
                    limit=1
                )
                vals['roll_no'] = (last_student.roll_no or 0) + 1

        return super().create(vals_list)

    #write method of Model(Prevents change in Admission date)
    def write(self,vals):
        if 'addmission' in vals:
            raise ValidationError("Admission Date Can't be Modified")
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _check_student_delete(self):
        for rec in self:
            if rec.roll_no:
                raise ValidationError("Can't Delete the Students whom RollNos are Assigned")



class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "School Teacher"

    name = fields.Char(required=True)
    employee_id = fields.Char(string="Employee ID", required=True)
    qualification = fields.Char(string="Qualification")
    experience_years = fields.Float(string="Experience (Years)")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    status = fields.Boolean(string="Active", default=False)

    @api.constrains('email')
    def _check_email(self):
        pattern=r"[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[com| in| co.in]"
        for record in self:
            if record.email:
                if not re.match(pattern,record.email):
                    raise ValidationError("Must Match Email Pattern")

    @api.constrains('phone')
    def _check_phone(self):
        pattern=r"^\+?\d{10,15}$"
        for rec in self:
            if rec.phone:
                if not re.match(pattern,rec.phone):
                    raise ValidationError("Phone Format Invalid")



class SchoolClass(models.Model):
    _name = "school.class"
    _description = "School Class"

    name = fields.Char(string="Class Name", required=True)
    grade = fields.Char(string="Grade")
    section = fields.Char(string="Section")
    academic_year = fields.Char(string="Academic Year")
    fees_count=fields.Integer(compute="_compute_fees_count")


    student_ids = fields.One2many(
        "school.student",
        "class_id",
        string="Students"
    )

    def _compute_fees_count(self):
        for rec in self:
            rec.fees_count=self.env['school.fees'].search_count([('student_id','=',rec.id)])

    

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

    # -------------------------
    # SMART BUTTON ACTIONS
    # -------------------------

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': 'Students',
            'type': 'ir.actions.act_window',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': [('class_id', '=', self.id)],
            'context': {'default_class_id': self.id},
        }

    def action_view_fees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fees',
            'res_model': 'school.fees',
            'view_mode': 'list,form',
            'domain': [('class_id', '=', self.id)],
        }











'''
	fees=fields.Monetary(string="Fees")
	class_id=fields.Many2one("school.class",string="Class")
	teacher_id=fields.Many2many("school.teacher",string="Teachers")
	notes=fields.Html(string="Notes")
	image=fields.Binary(string="Image")


class schoolclass(models.Model):
	_name="school.class"
	_description="School Class"

	name = fields.Char(string="Class Name", required=True)
    section = fields.Char(string="Section")


 class schoolteacher(models.Model):
	_name="school.teacher"
	_description="School Teacher"

	name=fields.Char(string="Name",required)
	subject=fields.Char(string="Subject Name")
'''
