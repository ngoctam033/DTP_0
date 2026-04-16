from odoo import fields, models


class DtpSchool(models.Model):
    _name = 'dtp.school'
    _description = 'School'
    _order = 'name'

    name = fields.Char(string='Tên trường', required=True)
    code = fields.Char(string='Mã trường')
    partner_id = fields.Many2one('res.partner', string='Liên hệ')
    manager_name = fields.Char(string='Người phụ trách')
    phone = fields.Char(string='Điện thoại')
    email = fields.Char(string='Email')
    note = fields.Text(string='Ghi chú')
    class_ids = fields.One2many('dtp.school.class', 'school_id', string='Lớp học')


class DtpSchoolSubject(models.Model):
    _name = 'dtp.school.subject'
    _description = 'School Subject'
    _order = 'name'

    name = fields.Char(string='Tên môn học', required=True)
    code = fields.Char(string='Mã môn')
    description = fields.Text(string='Mô tả')


class DtpSchoolClass(models.Model):
    _name = 'dtp.school.class'
    _description = 'School Class'
    _order = 'school_id, name'

    name = fields.Char(string='Tên lớp', required=True)
    code = fields.Char(string='Mã lớp')
    school_id = fields.Many2one('dtp.school', string='Trường học', required=True)
    grade_level = fields.Char(string='Khối lớp')
    homeroom_teacher = fields.Char(string='Giáo viên phụ trách')
    student_count = fields.Integer(string='Sĩ số')
    subject_ids = fields.Many2many('dtp.school.subject', string='Môn học')
    toolkit_ids = fields.Many2many('dtp.teaching.kit', string='Bộ dụng cụ')
    note = fields.Text(string='Ghi chú')
