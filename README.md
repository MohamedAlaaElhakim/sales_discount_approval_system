# Sales Discount Approval System

Enhanced Odoo module for managing discount approvals on sales orders with a complete workflow.

## Features

### ✅ What's Fixed from Original Version

1. **Request Approval Button**: Added missing button for sales users to request approval
2. **Proper Reject Wizard**: Fixed reject button to open wizard for entering reason
3. **Configurable Threshold**: Moved discount threshold to Settings (was hardcoded at 20%)
4. **Notifications System**: Added email and in-app notifications for all actions
5. **Activity Tracking**: Automatic activities created for managers
6. **Complete Workflow**: Full approval lifecycle with history tracking

### 🎯 Core Functionality

- **Discount Threshold Configuration**: Set company-specific discount approval threshold in Settings
- **Request Approval**: Sales users request approval when discount exceeds threshold
- **Manager Approval/Rejection**: Managers can approve or reject with reason
- **Email Notifications**: Automatic emails sent to relevant parties
- **Approval History**: Complete audit trail of all approval actions
- **Smart Buttons**: Context-aware buttons shown based on state and user role
- **Chatter Integration**: All actions logged in order chatter

### 📊 Approval States

- **None**: No approval needed (discount within threshold)
- **Waiting**: Approval requested, pending manager action
- **Approved**: Discount approved by manager
- **Rejected**: Discount rejected with reason

### 🔒 Security Groups

1. **Discount User**: Can request approval, view own orders
2. **Discount Manager**: Can approve/reject, view approval history

## Installation

1. Copy module to Odoo addons directory
2. Update apps list
3. Install "Sales Discount Approval System"
4. Configure threshold in Settings > Sales > Discount Approval Threshold

## Configuration

### Set Discount Threshold

1. Go to: **Settings > Sales**
2. Find: **Discount Approval Threshold (%)**
3. Set your desired percentage (default: 20%)
4. Save

### Assign User Groups

1. Go to: **Settings > Users & Companies > Users**
2. Select user
3. Assign groups:
   - **Discount User**: For sales team members
   - **Discount Manager**: For managers who approve

## Usage Workflow

### For Sales Users

1. Create sales order
2. Add products with discounts
3. If discount > threshold:
   - Click **"Request Approval"** button
   - Order state changes to "Waiting"
   - Manager receives notification
4. Wait for manager decision
5. If approved: Confirm order
6. If rejected: Adjust discount or discuss with manager

### For Managers

1. Receive notification of pending approval
2. Open sales order
3. Review discount details
4. Decision:
   - **Approve**: Click "Approve Discount" button
   - **Reject**: Click "Reject Discount", enter reason
5. Salesperson receives notification

## Views & Reports

### Sales Orders

- **Tree View**: Shows approval state badge
- **Form View**: 
  - Approval statusbar in header
  - Context-aware action buttons
  - Discount info group showing max discount vs threshold
  - Approval history tab
- **Filters**:
  - Waiting Approval
  - Approved
  - Rejected
- **Group By**: Approval State

### Approval History

- **Menu**: Sales > Approval History
- **Access**: Discount Managers only
- **Features**:
  - View all approval actions
  - Filter by action type, user, date
  - Group by various fields
  - Cannot delete records (audit trail)

## Technical Details

### Models

#### sale.order (inherited)
- `approval_state`: Selection field for approval workflow
- `approver_id`: User who approved/rejected
- `max_line_discount`: Computed max discount across order lines
- `discount_threshold`: Related company threshold
- `show_request_approval`: Computed visibility field
- `show_approve_reject`: Computed visibility field

#### sale.order.approval (new)
- `order_id`: Related sales order
- `user_id`: User who performed action
- `action`: requested/approved/rejected
- `reason`: Text reason/notes
- `date`: Timestamp
- `discount_percentage`: Snapshot of discount at action time

#### res.company (inherited)
- `discount_approval_threshold`: Company-specific threshold

### Methods

- `action_request_approval()`: Request approval from manager
- `action_approve_discount()`: Approve discount request
- `action_open_reject_wizard()`: Open rejection wizard
- `action_reject_discount(reason)`: Reject with reason
- `_notify_managers()`: Send notification to managers
- `_notify_salesperson(action, reason)`: Notify sales user
- `action_confirm()`: Override to check approval

### Notifications

- **Email Templates**: 3 templates for request/approve/reject
- **Activities**: Auto-created for managers
- **Chatter Messages**: Posted for all actions

## Improvements Over Original

| Feature | Original | Improved |
|---------|----------|----------|
| Request Approval | ❌ Missing | ✅ Added |
| Reject Wizard | ❌ Not working | ✅ Fixed |
| Threshold Config | ❌ Hardcoded | ✅ In Settings |
| Notifications | ❌ None | ✅ Email + In-app |
| Activities | ❌ None | ✅ Auto-created |
| Approval History | ✅ Basic | ✅ Enhanced |
| Button Visibility | ❌ Static | ✅ Dynamic |
| Discount Tracking | ❌ No snapshot | ✅ Stored in history |

## Best Practices

1. **Set Realistic Threshold**: Based on company policy and profit margins
2. **Regular Reviews**: Monitor approval history for patterns
3. **Clear Rejection Reasons**: Help sales team understand and improve
4. **Training**: Ensure sales team understands workflow
5. **Manager Availability**: Ensure managers check notifications regularly

## Troubleshooting

### Issue: Request Approval button not showing
- Check discount exceeds threshold
- Order must be in draft state
- User must have Discount User group

### Issue: Cannot confirm order
- Check approval state is "approved"
- If rejected, adjust discount or request new approval
- If waiting, ask manager to review

### Issue: Manager not receiving notifications
- Check user has Discount Manager group
- Check email settings configured
- Check notification preferences

## Support & Contribution

For issues, improvements, or questions:
- Create issue in repository
- Submit pull requests for enhancements
- Contact: [Your contact info]

## License

LGPL-3

## Version History

### v17.0.2.0.0 (Improved Version)
- ✅ Added request approval functionality
- ✅ Fixed reject wizard
- ✅ Made threshold configurable
- ✅ Added notifications system
- ✅ Enhanced approval history
- ✅ Improved UI/UX

### v17.0.1.0.0 (Original Version)
- Basic approval workflow
- Static threshold
- Limited functionality

---

**Made with ❤️ for Odoo Community**
# sales_discount_approval_system
