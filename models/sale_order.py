from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_state = fields.Selection([
        ("none", "No Approval Needed"),
        ("waiting", "Waiting Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ],
        string="Discount Approval",
        default="none",
        tracking=True,
        copy=False,
    )

    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        help="The manager who approved/rejected the discount on this sales order.",
        copy=False,
        tracking=True,
    )

    approval_history_ids = fields.One2many(
        "sale.order.approval",
        "order_id",
        string="Approval History",
        copy=False,
    )

    max_line_discount = fields.Float(
        string="Max Line Discount (%)",
        compute="_compute_max_line_discount",
        store=True,
    )

    discount_threshold = fields.Float(
        string="Discount Threshold",
        compute="_compute_discount_threshold",
    )

    show_request_approval = fields.Boolean(
        string="Show Request Approval",
        compute="_compute_show_request_approval",
    )

    show_approve_reject = fields.Boolean(
        string="Show Approve/Reject",
        compute="_compute_show_approve_reject",
    )

    @api.depends("order_line.discount")
    def _compute_max_line_discount(self):
        for order in self:
            discounts = order.order_line.mapped("discount")
            order.max_line_discount = max(discounts) if discounts else 0.0

    # تم إضافة api.depends لتحديث القيمة تلقائياً إذا تغيرت إعدادات الشركة
    @api.depends("company_id.discount_approval_threshold")
    def _compute_discount_threshold(self):
        """Get threshold from company settings"""
        for order in self:
            order.discount_threshold = (
                    order.company_id.discount_approval_threshold or 20.0
            )

    # تم إضافة حالة الطلب (state) للاعتماديات حتى يختفي الزر بعد تأكيد الطلب
    @api.depends("approval_state", "max_line_discount", "discount_threshold", "state")
    def _compute_show_request_approval(self):
        """Show request approval button if discount exceeds threshold and not yet requested"""
        for order in self:
            order.show_request_approval = (
                    order.max_line_discount > order.discount_threshold
                    and order.approval_state == "none"
                    and order.state == "draft"
            )

    # تم إضافة depends و depends_context ليعمل الزر بشكل ديناميكي حسب صلاحيات المستخدم
    @api.depends("approval_state")
    @api.depends_context('uid')
    def _compute_show_approve_reject(self):
        """Show approve/reject buttons for managers"""
        discount_manager = self.env.user.has_group(
            "sales_discount_approval_system.group_discount_manager"
        )
        for order in self:
            order.show_approve_reject = (
                    discount_manager and order.approval_state == "waiting"
            )

    def _need_discount_approval(self):
        """Return True if any line discount exceeds threshold"""
        self.ensure_one()
        return self.max_line_discount > self.discount_threshold

    @api.onchange("order_line")
    def _onchange_order_line_discount(self):
        """Auto-reset approval state if discount changes after approval"""
        warning_res = {}
        for order in self:
            # نتأكد أن الطلب لم يتم تأكيده بعد
            if order.approval_state in ("approved", "rejected") and order.state in ("draft", "sent"):
                if order._need_discount_approval():
                    order.approval_state = "none"
                    # تم إصلاح الخطأ المتمثل في الـ return داخل حلقة الـ for
                    warning_res = {
                        'warning': {
                            'title': _("Approval Reset"),
                            'message': _(
                                "The discount has been modified. "
                                "The previous approval is no longer valid. "
                                "Please request approval again."
                            ),
                        }
                    }
        if warning_res:
            return warning_res

    def write(self, vals):
        """Override write to handle discount changes after approval"""
        # [إصلاح حرج] نقوم بحفظ قيم الخصم القديمة قبل التعديل لمقارنتها لاحقاً
        old_discounts = {order.id: order.max_line_discount for order in self}

        res = super().write(vals)

        # نتحقق مما إذا كان التعديل قد شمل أسطر الطلب
        if 'order_line' in vals:
            for order in self:
                # لا نلغي الموافقة إلا إذا كان الطلب مبدئياً وتمت الموافقة عليه أو رفضه مسبقاً
                if order.approval_state in ("approved", "rejected") and order.state in ("draft", "sent"):
                    new_discount = order.max_line_discount
                    old_discount = old_discounts.get(order.id, 0.0)

                    # [الشرط الأهم] لا نلغي الموافقة إلا إذا تغيرت نسبة الخصم بالفعل!
                    # الكود القديم كان يلغي الموافقة بمجرد تغيير الكمية أو الوصف
                    if new_discount != old_discount and order._need_discount_approval():
                        order.write({
                            'approval_state': 'none',
                            'approver_id': False
                        })
                        order.message_post(
                            body=_(
                                "Discount modified from %.2f%% to %.2f%% after %s. Approval reset. "
                                "Please request approval again."
                            ) % (old_discount, new_discount, order.approval_state),
                            message_type="notification",
                        )
        return res

    def action_confirm(self):
        """Block confirmation if approval required but not approved"""
        for order in self:
            if order._need_discount_approval():
                if order.approval_state == "none":
                    raise UserError(
                        _(
                            "This order has a discount of %.2f%% which exceeds the threshold of %.2f%%. "
                            "Please request approval before confirming."
                        )
                        % (order.max_line_discount, order.discount_threshold)
                    )
                elif order.approval_state == "waiting":
                    raise UserError(
                        _("You cannot confirm this order while approval is pending.")
                    )
                elif order.approval_state == "rejected":
                    raise UserError(
                        _(
                            "You cannot confirm this order. The discount has been rejected. "
                            "Please adjust the discount or request a new approval."
                        )
                    )
        return super().action_confirm()

    def action_request_approval(self):
        """Request discount approval from manager"""
        for order in self:
            if not order._need_discount_approval():
                raise UserError(
                    _(
                        "Discount approval is not required. The maximum discount (%.2f%%) "
                        "is within the allowed threshold (%.2f%%)."
                    )
                    % (order.max_line_discount, order.discount_threshold)
                )

            order.write({"approval_state": "waiting"})

            self.env["sale.order.approval"].create(
                {
                    "order_id": order.id,
                    "user_id": self.env.user.id,
                    "action": "requested",
                    "reason": "Approval requested for %.2f%% discount"
                              % order.max_line_discount,
                }
            )

            order._notify_managers()

            order.message_post(
                body=_(
                    "Discount approval requested by %s for %.2f%% discount (threshold: %.2f%%)"
                )
                     % (self.env.user.name, order.max_line_discount, order.discount_threshold),
                message_type="notification",
            )

    def action_approve_discount(self):
        """Approve discount request"""
        for order in self:
            if order.approval_state != "waiting":
                raise UserError(_("This order is not waiting for approval."))

            order.write(
                {
                    "approval_state": "approved",
                    "approver_id": self.env.user.id,
                }
            )

            self.env["sale.order.approval"].create(
                {
                    "order_id": order.id,
                    "user_id": self.env.user.id,
                    "action": "approved",
                    "reason": "Discount approved by manager",
                }
            )

            order._notify_salesperson("approved")

            order.message_post(
                body=_("Discount of %.2f%% approved by %s")
                     % (order.max_line_discount, self.env.user.name),
                message_type="notification",
            )

    def action_open_reject_wizard(self):
        """Open wizard to enter rejection reason"""
        self.ensure_one()
        return {
            "name": _("Reject Discount"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }

    def action_reject_discount(self, reason=None):
        """Reject discount request"""
        for order in self:
            if order.approval_state != "waiting":
                raise UserError(_("This order is not waiting for approval."))

            if not reason:
                reason = "Rejected by manager"

            order.write(
                {
                    "approval_state": "rejected",
                    "approver_id": self.env.user.id,
                }
            )

            self.env["sale.order.approval"].create(
                {
                    "order_id": order.id,
                    "user_id": self.env.user.id,
                    "action": "rejected",
                    "reason": reason,
                }
            )

            order._notify_salesperson("rejected", reason)

            order.message_post(
                body=_("Discount of %.2f%% rejected by %s. Reason: %s")
                     % (order.max_line_discount, self.env.user.name, reason),
                message_type="notification",
            )

    def _notify_managers(self):
        """Send notification to discount managers"""
        self.ensure_one()

        managers = self.env.ref(
            "sales_discount_approval_system.group_discount_manager"
        ).users

        if not managers:
            raise UserError(_("No discount managers found. Please assign users to the 'Discount Manager' group."))

        self.message_subscribe(partner_ids=managers.mapped("partner_id").ids)

        for manager in managers:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("Discount Approval Required"),
                note=_(
                    "Sales Order %s requires approval for %.2f%% discount (threshold: %.2f%%)"
                ) % (self.name, self.max_line_discount, self.discount_threshold),
                user_id=manager.id,
            )

        template = self.env.ref(
            'sales_discount_approval_system.email_template_approval_request',
            raise_if_not_found=False
        )
        if template:
            for manager in managers:
                if manager.email:
                    # جعل force_send=False لتفادي بطء أو تعليق النظام إذا كان عدد المدراء كبيراً
                    template.send_mail(
                        self.id,
                        email_values={
                            'email_to': manager.email,
                            'recipient_ids': [(4, manager.partner_id.id)]
                        },
                        force_send=False
                    )

    def _notify_salesperson(self, action, reason=None):
        """Send notification to salesperson"""
        self.ensure_one()

        if not self.user_id:
            return

        body = _("Your discount request for order %s has been %s") % (self.name, action)
        if reason:
            body += _(" with reason: %s") % reason

        self.message_post(
            body=body,
            partner_ids=[self.user_id.partner_id.id],
            message_type="notification",
        )

        if action == "approved":
            template = self.env.ref(
                'sales_discount_approval_system.email_template_approval_granted',
                raise_if_not_found=False
            )
        else:
            template = self.env.ref(
                'sales_discount_approval_system.email_template_approval_rejected',
                raise_if_not_found=False
            )

        if template and self.user_id.email:
            template.send_mail(
                self.id,
                email_values={'recipient_ids': [(4, self.user_id.partner_id.id)]},
                force_send=False
            )