from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderApproval(models.Model):
    _name = "sale.order.approval"
    _description = "Sale Order Approval History"
    _order = "date desc"
    _rec_name = "order_id"

    order_id = fields.Many2one(
        "sale.order",
        string="Sales Order",
        required=True,
        ondelete="cascade",
        index=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        index=True,
    )

    action = fields.Selection([
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Action",
        required=True,
    )

    reason = fields.Text(
        string="Reason/Notes",
        help="Reason for approval or rejection, or notes about the request.",
    )

    date = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        required=True,
        index=True,
        readonly=True, # تم إضافة readonly
    )

    order_partner_id = fields.Many2one(
        related="order_id.partner_id",
        string="Customer",
        store=True,
    )

    order_amount_total = fields.Monetary(
        related="order_id.amount_total",
        string="Order Total",
        store=True,
    )

    currency_id = fields.Many2one(
        related="order_id.currency_id",
        string="Currency",
        store=True, # [إصلاح حرج] يجب أن يكون محفوظاً طالما الحقل المالي محفوظ
    )

    discount_percentage = fields.Float(
        string="Discount %",
        help="Maximum discount percentage on the order at time of action",
    )

    def unlink(self):
        """Prevent deleting approval history (audit trail)"""
        raise UserError(
            _("You cannot delete approval history records. This is an audit trail.")
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Add discount percentage automatically"""
        #[إصلاح] التعامل مع الحالات التي قد يغيب فيها order_id في البداية
        records = super().create(vals_list)
        for record in records:
            if not record.discount_percentage and record.order_id:
                record.discount_percentage = record.order_id.max_line_discount
        return records