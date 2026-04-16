from odoo import api, fields, models


class DtpSchool(models.Model):
    _name = 'dtp.school'
    _description = 'School'
    _order = 'name'

    name = fields.Char(string='Tên trường', required=True)
    code = fields.Char(string='Mã trường')
    manager_name = fields.Char(string='Người phụ trách')
    phone = fields.Char(string='Điện thoại')
    email = fields.Char(string='Email')
    location_region = fields.Selection([
        ('hcm', 'HCM'),
        ('mekong', 'Mekong'),
        ('hue', 'Huế'),
    ], string='Vùng')
    province_name = fields.Char(
        string='Tỉnh/Quận',
        help='Nếu vùng là HCM thì nhập quận; các vùng khác nhập tỉnh.',
    )
    address_detail = fields.Char(string='Địa chỉ cụ thể')
    school_level = fields.Selection([
        ('kindergarten', 'Mầm non'),
        ('primary', 'Tiểu học'),
        ('secondary', 'Trung học (cấp 2)'),
    ], string='Cấp học')
    salesperson_ids = fields.Many2many(
        'dtp.school.salesperson',
        'dtp_school_salesperson_rel',
        'school_id',
        'salesperson_id',
        string='Sale phụ trách',
    )
    note = fields.Text(string='Ghi chú')
    class_ids = fields.One2many('dtp.school.class', 'school_id', string='Lớp học')


class DtpSchoolSalesperson(models.Model):
    _name = 'dtp.school.salesperson'
    _description = 'School Salesperson'
    _order = 'name'

    name = fields.Char(string='Tên sale', required=True)
    phone = fields.Char(string='Điện thoại')
    email = fields.Char(string='Email')
    note = fields.Text(string='Ghi chú')


class DtpSchoolGrade(models.Model):
    _name = 'dtp.school.grade'
    _description = 'School Grade'
    _order = 'sequence, name'

    name = fields.Char(string='Khối/Lớp', required=True)
    school_level = fields.Selection([
        ('kindergarten', 'Mầm non'),
        ('primary', 'Tiểu học'),
        ('secondary', 'Trung học (cấp 2)'),
    ], string='Cấp học', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)


class DtpSchoolSubject(models.Model):
    _name = 'dtp.school.subject'
    _description = 'School Subject'
    _order = 'name'

    name = fields.Char(string='Tên môn học', required=True)
    code = fields.Char(string='Mã môn')
    description = fields.Text(string='Mô tả')
    equipment_line_ids = fields.One2many('dtp.school.subject.equipment', 'subject_id', string='Dụng cụ học tập')


class DtpSchoolSubjectEquipment(models.Model):
    _name = 'dtp.school.subject.equipment'
    _description = 'School Subject Equipment'
    _order = 'id'

    subject_id = fields.Many2one('dtp.school.subject', string='Môn học', required=True, ondelete='cascade')
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Dụng cụ / Thiết bị',
        required=True,
        domain=[('is_teaching_product', '=', True)],
    )
    quantity = fields.Float(string='Số lượng đề xuất', default=1.0, required=True)
    note = fields.Char(string='Ghi chú')


class DtpSchoolClass(models.Model):
    _name = 'dtp.school.class'
    _description = 'School Class'
    _order = 'school_id, name'

    name = fields.Char(string='Tên lớp', required=True)
    code = fields.Char(string='Mã lớp')
    school_id = fields.Many2one('dtp.school', string='Trường học', required=True)
    school_level = fields.Selection(related='school_id.school_level', string='Cấp học', store=True, readonly=True)
    grade_id = fields.Many2one(
        'dtp.school.grade',
        string='Khối/Lớp',
        domain="[('school_level', '=', school_level)]",
        required=True,
    )
    grade_level = fields.Char(string='Khối lớp', related='grade_id.name', store=True, readonly=True)
    homeroom_teacher = fields.Char(string='Giáo viên phụ trách')
    student_count = fields.Integer(string='Sĩ số')
    subject_ids = fields.Many2many('dtp.school.subject', string='Môn học')
    toolkit_ids = fields.Many2many('dtp.teaching.kit', string='Bộ dụng cụ')
    note = fields.Text(string='Ghi chú')

    @api.onchange('school_id')
    def _onchange_school_id(self):
        if self.grade_id and self.school_level and self.grade_id.school_level != self.school_level:
            self.grade_id = False

    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        if self.grade_id and not self.name:
            self.name = self.grade_id.name
