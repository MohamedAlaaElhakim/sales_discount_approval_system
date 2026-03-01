from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    # إضافة الحقل على مستوى الشركة لدعم تعدد الشركات (Multi-Company)
    discount_approval_threshold = fields.Float(
        string="Discount Approval Threshold (%)",
        default=0.20,  # في Odoo 17 من الأفضل تخزين النسب المئوية ككسور عشرية (0.20 تعني 20%)
        help="Orders with discount exceeding this percentage will require manager approval",
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ربط الحقل بإعدادات الشركة الحالية
    discount_approval_threshold = fields.Float(
        related="company_id.discount_approval_threshold",
        string="Discount Approval Threshold (%)",
        readonly=False, # مهم جداً في Odoo 17 للسماح بتعديل الحقل الـ related
        help="Orders with discount exceeding this percentage will require manager approval",
    )