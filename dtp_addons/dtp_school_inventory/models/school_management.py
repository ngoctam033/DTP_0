# -*- coding: utf-8 -*-

from odoo import fields, models


class DtpSchool(models.Model):
    _inherit = 'res.partner'
    _description = 'School'

    name = fields.Char(required=True)
    is_school = fields.Boolean(string='Is School')
    school_type = fields.Selection(
        selection=[
            ('kindergarten', 'Mam non'),
            ('primary', 'Cap 1'),
            ('secondary', 'Cap 2'),
        ],
        string='School Type',
        required=True,
    )
    address = fields.Char(required=True)
    district = fields.Char(required=True)
    province = fields.Char(required=True)
    region = fields.Selection(
        selection=[
            ('hcm', 'HCM'),
            ('mekong', 'Mekong'),
            ('hue', 'Hue'),
        ],
        required=True,
    )
    sale_user_ids = fields.Many2many(
        'res.users',
        'res_partner_sale_user_rel',
        'partner_id',
        'user_id',
        string='Salespersons',
    )
    class_ids = fields.One2many('res.partner.class', 'school_id', string='Classes')


class DtpSchoolClass(models.Model):
    _name = 'res.partner.class'
    _description = 'School Class'
    _rec_name = 'grade'

    class_count = fields.Integer(string='Class Count', required=True, default=1)
    grade = fields.Selection(
        selection=[
            ('a0', 'A0'),
            ('a1', 'A1'),
            ('a2', 'A2'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
        ],
        required=True,
    )
    school_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    subject_ids = fields.Many2many(
        'res.partner.subject',
        'res_partner_class_subject_rel',
        'class_id',
        'subject_id',
        string='Subjects',
    )
    region = fields.Selection(related='school_id.region', store=True)


class DtpSchoolSubject(models.Model):
    _name = 'res.partner.subject'
    _description = 'Class Subject'

    name = fields.Char(required=True)
    class_ids = fields.Many2many(
        'res.partner.class',
        'res_partner_class_subject_rel',
        'subject_id',
        'class_id',
        string='Classes',
    )
    supply_product_ids = fields.Many2many('product.product', string='Learning Supplies')
