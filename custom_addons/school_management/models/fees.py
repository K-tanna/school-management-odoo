from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolFees(models.Model):
    _name = "school.fees"
    _description = "Student Fees Ledger"
    _rec_name = "student_id"

    student_id = fields.Many2one("school.student", required=True)
    class_id = fields.Many2one(
        "school.class", related="student_id.class_id", store=True
    )

    amount = fields.Monetary(required=True)
    paid_amount = fields.Monetary(
        compute="_compute_paid", store=True
    )
    due_amount = fields.Monetary(
        compute="_compute_due", store=True
    )
    payment_mode=fields.Selection(
        [('upi', 'UPi'),
         ('cash', 'Cash'),
         ('card', 'Card')],
        store=True
    )
    status = fields.Selection(
        [('draft', 'Draft'),
         ('partial', 'Partially Paid'),
         ('paid', 'Fully Paid')],
        compute="_compute_status",
        store=True
    )

    payment_ids = fields.One2many(
        "school.fees.payment",
        "fees_id",
        string="Payments"
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    # -------------------------
    # COMPUTES
    # -------------------------

    @api.depends('payment_ids.amount')
    def _compute_paid(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_ids.mapped('amount'))

    @api.depends('amount', 'paid_amount')
    def _compute_due(self):
        for rec in self:
            rec.due_amount = rec.amount - rec.paid_amount

    @api.depends('amount', 'paid_amount')
    def _compute_status(self):
        for rec in self:
            if rec.paid_amount == 0:
                rec.status = 'draft'
            elif rec.paid_amount < rec.amount:
                rec.status = 'partial'
            else:
                rec.status = 'paid'

    @api.constrains('amount')
    def _check_total_fees(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Total fees must be greater than zero.")

'''    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'school.fees.payment',
            'view_mode': 'list,form',
            'domain': [('fees_id', '=', self.id)],
            'context': {
                'default_fees_id': self.id,
                'default_student_id': self.student_id.id,
            },
        }'''


class SchoolFeesPayment(models.Model):
    _name = "school.fees.payment"
    _description = "Fees Payment"

    name = fields.Char(
        string="Receipt No",
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'school.fees.payment'
        )
    )

    fees_id = fields.Many2one(
        "school.fees",
        required=True,
        ondelete="cascade"
    )

    student_id = fields.Many2one(
        related="fees_id.student_id",
        store=True
    )

    class_id = fields.Many2one(
        related="fees_id.class_id",
        store=True
    )

    date = fields.Date(default=fields.Date.today)

    amount = fields.Monetary(required=True)

    payment_mode = fields.Selection(
        [('cash', 'Cash'), ('upi', 'UPI'), ('card', 'Card')]
    )

    currency_id = fields.Many2one(
        related="fees_id.currency_id",
        store=True
    )

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be greater than zero.")

'''    @api.constrains('amount', 'fees_id')
    def _check_overpayment(self):
        for rec in self:
            if rec.fees_id and rec.amount > rec.fees_id.due_amount:
                raise ValidationError(
                    f"Payment cannot exceed due amount ({rec.fees_id.due_amount})."
                )'''
