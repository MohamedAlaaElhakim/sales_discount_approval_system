from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RejectReasonWizard(models.TransientModel):
    _name = "sale.order.reject.wizard"
    _description = "Discount Rejection Wizard"

    order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        required=True,
        readonly=True,
    )

    partner_id = fields.Many2one(
        related="order_id.partner_id",
        string="Customer",
        readonly=True,
    )

    max_discount = fields.Float(
        related="order_id.max_line_discount",
        string="Discount (%)",
        readonly=True,
    )

    reason = fields.Text(
        string="Rejection Reason",
        required=True,
        help="Please provide a clear reason for rejecting this discount request",
    )

    def action_confirm_reject(self):
        """Confirm rejection with reason"""
        self.ensure_one()

        if not self.reason or not self.reason.strip():
            raise UserError(_("Please provide a rejection reason."))

        # [تحسين] نمرر الصلاحية لضمان عدم حدوث خطأ عند تعديل الطلب من المعالج
        self.order_id.sudo().action_reject_discount(reason=self.reason)

        return {"type": "ir.actions.act_window_close"}