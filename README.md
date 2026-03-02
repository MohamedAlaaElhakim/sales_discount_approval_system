# 🛡️ Sales Discount Approval System

> Smart discount approval workflow for Odoo 17 with configurable thresholds, automated notifications, and complete audit trail.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Odoo](https://img.shields.io/badge/Odoo_17-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![License](https://img.shields.io/badge/License-LGPL--3-blue?style=for-the-badge)

-----

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Module Structure](#module-structure)
- [Models](#models)
- [Workflow](#workflow)
- [Security](#security)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Email Notifications](#email-notifications)
- [Dependencies](#dependencies)
- [Demo Data](#demo-data)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

-----

## 🧩 Overview

The **Sales Discount Approval System** is a powerful Odoo 17 module that adds a professional approval workflow for sales order discounts. When a salesperson applies a discount that exceeds your company’s threshold, the system automatically triggers an approval process with managers, complete with email notifications and full audit trail.

**Perfect for:** Companies that need to control discount approvals, maintain pricing discipline, track approval history, and ensure discounts are authorized by management before order confirmation.

-----

## ✨ Key Features

### 🎯 Smart Discount Control

- **Configurable Threshold** - Set company-wide discount limits (e.g., 20%)
- **Auto-Detection** - Automatically detects when discounts exceed threshold
- **Block Confirmation** - Prevents order confirmation without proper approval
- **Real-Time Validation** - Instant validation as discounts are applied

### 🔄 Approval Workflow

- **Request Approval** - One-click approval request from sales orders
- **Manager Dashboard** - Dedicated buttons for approve/reject actions
- **Approval States** - Clear status tracking (None, Waiting, Approved, Rejected)
- **State Management** - Auto-reset approval if discount changes after approval

### 📧 Automated Notifications

- **Manager Alerts** - Email and activity notifications to all discount managers
- **Salesperson Updates** - Automatic notifications on approval/rejection
- **Chatter Integration** - All actions logged in order chatter
- **Activity Scheduling** - Creates to-do activities for managers

### 📊 Audit Trail

- **Complete History** - Track every approval request, approval, and rejection
- **Timestamp Records** - Date and time for all actions
- **User Tracking** - Who requested, who approved/rejected
- **Reason Logging** - Store rejection reasons for reference
- **Immutable Records** - History cannot be deleted (audit compliance)

### 🔐 Security & Permissions

- **Role-Based Access** - Two user groups: Discount User and Discount Manager
- **Permission Control** - Users can only see appropriate buttons
- **Group Management** - Easy assignment of managers
- **Record Rules** - Built-in security rules

-----

## 🔄 How It Works

### The Approval Flow:

```
1. Salesperson creates quotation
   ↓
2. Applies discount > threshold (e.g., 25% when limit is 20%)
   ↓
3. System shows "Request Approval" button
   ↓
4. Click → Managers receive email + activity notification
   ↓
5. Manager reviews and approves/rejects
   ↓
6. Salesperson notified of decision
   ↓
7. If approved → Can confirm order
   If rejected → Must adjust discount or re-request
```

### Key Behaviors:

- ✅ **Threshold Check** - Only discounts exceeding threshold require approval
- 🔒 **Confirmation Block** - Cannot confirm unapproved orders
- 🔄 **Auto-Reset** - Changes to discount after approval reset the state
- 📧 **Multi-Manager** - All managers in the group are notified
- 📝 **Rejection Wizard** - Requires reason when rejecting

-----

## 📁 Module Structure

```
sales_discount_approval_system/
├── models/
│   ├── __init__.py
│   ├── sale_order.py              # Main approval logic & workflow
│   ├── approval_history.py        # Audit trail model
│   └── res_config_settings.py     # Company threshold configuration
│
├── wizard/
│   ├── __init__.py
│   ├── reject_reason_wizard.py    # Rejection reason entry
│   └── reject_reason_wizard_views.xml
│
├── views/
│   ├── sale_order_views.xml       # Enhanced sales order form
│   ├── approval_history_views.xml # Approval history list/form
│   └── res_config_settings_views.xml # Settings configuration
│
├── security/
│   ├── security.xml               # User groups definition
│   └── ir.model.access.csv        # Model access rights
│
├── data/
│   └── mail_template.xml          # Email notification templates
│
├── demo/
│   └── demo_data.xml              # Demo orders with various states
│
├── __init__.py
├── __manifest__.py
└── README.md
```

-----

## 🗂️ Models

### `sale.order` (Inherited)

Extended with approval workflow fields and methods.

**New Fields:**

```python
approval_state          # Selection: none, waiting, approved, rejected
approver_id            # Many2one: res.users (who approved/rejected)
approval_history_ids   # One2many: sale.order.approval
max_line_discount      # Float: highest discount % across all lines
discount_threshold     # Float: company threshold (computed)
show_request_approval  # Boolean: display request button (computed)
show_approve_reject    # Boolean: display manager buttons (computed)
```

**Key Methods:**

```python
action_request_approval()  # Request approval from managers
action_approve_discount()  # Approve the discount request
action_reject_discount()   # Reject with reason
_need_discount_approval()  # Check if approval needed
_notify_managers()         # Send notifications to managers
_notify_salesperson()      # Notify salesperson of decision
```

### `sale.order.approval`

Complete audit trail of all approval actions.

**Fields:**

```python
order_id              # Many2one: sale.order
user_id               # Many2one: res.users (who performed action)
action                # Selection: requested, approved, rejected
reason                # Text: notes or rejection reason
date                  # Datetime: timestamp (auto-set, readonly)
order_partner_id      # Many2one: customer (related, stored)
order_amount_total    # Monetary: order total (related, stored)
currency_id           # Many2one: order currency (related, stored)
discount_percentage   # Float: discount at time of action
```

**Security:**

- Records cannot be deleted (audit compliance)
- Auto-captures discount percentage on creation

### `res.company` & `res.config.settings` (Inherited)

**Added Field:**

```python
discount_approval_threshold  # Float: company discount limit %
```

-----

## 🔄 Workflow

### Approval States:

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  none (No Approval Needed)                      │
│    └─► Discount ≤ Threshold                     │
│    └─► Or no discount applied                   │
│                                                 │
│  waiting (Waiting Approval)                     │
│    └─► Request sent to managers                 │
│    └─► Awaiting decision                        │
│                                                 │
│  approved (Approved)                            │
│    └─► Manager approved                         │
│    └─► Can confirm order                        │
│                                                 │
│  rejected (Rejected)                            │
│    └─► Manager rejected with reason             │
│    └─► Must adjust or re-request                │
│                                                 │
└─────────────────────────────────────────────────┘
```

### State Transitions:

|From    |To      |Trigger                |Who        |
|--------|--------|-----------------------|-----------|
|none    |waiting |Request Approval button|Salesperson|
|waiting |approved|Approve button         |Manager    |
|waiting |rejected|Reject button          |Manager    |
|approved|none    |Discount changed (auto)|System     |
|rejected|none    |Discount changed (auto)|System     |

### Validation Rules:

- ❌ Cannot confirm order if `approval_state = "none"` and discount > threshold
- ❌ Cannot confirm order if `approval_state = "waiting"`
- ❌ Cannot confirm order if `approval_state = "rejected"`
- ✅ Can confirm order if `approval_state = "approved"`
- ✅ Can confirm order if discount ≤ threshold (no approval needed)

-----

## 🔐 Security

### User Groups

|Group               |Access Level                           |Implied Groups              |
|--------------------|---------------------------------------|----------------------------|
|**Discount User**   |Can request approval for own discounts |Sales User                  |
|**Discount Manager**|Can approve/reject any discount request|Discount User, Sales Manager|

### Permissions by Group

**Discount User:**

- ✅ View own sales orders
- ✅ Apply discounts
- ✅ Request approval when needed
- ✅ See approval status
- ❌ Cannot approve/reject

**Discount Manager:**

- ✅ All Discount User permissions
- ✅ Approve discount requests
- ✅ Reject discount requests with reasons
- ✅ View all approval history
- ✅ Receive approval request notifications

### Model Access Rights

|Model               |Discount User|Discount Manager|
|--------------------|-------------|----------------|
|sale.order          |Read/Write   |Read/Write      |
|sale.order.approval |Read         |Read/Create     |
|reject.reason.wizard|None         |Read/Create     |

-----

## ⚙️ Installation

### Prerequisites

- Odoo 17.0 or higher
- PostgreSQL 12 or higher
- Python 3.10+

### Installation Steps

**1. Clone or download the module:**

```bash
cd /path/to/odoo/addons/
git clone https://github.com/YourUsername/sales_discount_approval_system.git
# or extract ZIP file here
```

**2. Restart Odoo server:**

```bash
sudo systemctl restart odoo
# or
./odoo-bin --config=/path/to/odoo.conf
```

**3. Update apps list:**

- Enable **Developer Mode** → Settings → Activate the developer mode
- Go to **Apps → Update Apps List**

**4. Install the module:**

- Search for **Sales Discount Approval System**
- Click **Install**

**5. Module will automatically:**

- Create user groups
- Add fields to sales orders
- Create approval history model
- Set up email templates
- Load demo data (if enabled)

-----

## 🔧 Configuration

### Step 1: Set Discount Threshold

1. Go to **Settings → Sales**
1. Scroll to **Discount Approval** section
1. Set **Discount Approval Threshold (%)** (e.g., 20.0)
1. Click **Save**

> **Note:** Each company can have its own threshold (multi-company support)

### Step 2: Assign Managers

1. Go to **Settings → Users & Companies → Users**
1. Open a user who should approve discounts
1. Go to **Access Rights** tab
1. Under **Sales**, check **Discount Manager**
1. Save

> **Tip:** Assign multiple managers - all will receive notifications

### Step 3: Configure Email (Optional)

Ensure your Odoo instance has outgoing mail server configured:

1. **Settings → Technical → Outgoing Mail Servers**
1. Configure SMTP settings
1. Test connection

-----

## 🚀 Usage Guide

### For Salespeople:

#### Scenario 1: Discount Within Threshold

```
1. Create quotation
2. Add products with discount ≤ 20% (threshold)
3. No approval needed
4. Confirm order directly ✅
```

#### Scenario 2: Discount Exceeds Threshold

```
1. Create quotation
2. Add products with discount > 20% (e.g., 25%)
3. System shows "Request Approval" button
4. Click "Request Approval"
5. Status changes to "Waiting Approval"
6. Wait for manager decision
7. If approved → Confirm order ✅
8. If rejected → Adjust discount or contact manager
```

#### Scenario 3: Changing Discount After Approval

```
1. Order already approved (25% discount)
2. Change discount to 30%
3. System auto-resets approval to "none"
4. Warning message appears
5. Must request approval again
```

### For Managers:

#### Approving a Request

```
1. Receive email notification
2. Open sales order from email link or activity
3. Review discount details
4. Click "Approve Discount" button
5. Salesperson notified automatically ✅
```

#### Rejecting a Request

```
1. Receive email notification
2. Open sales order
3. Review discount details
4. Click "Reject Discount" button
5. Wizard opens → Enter rejection reason
6. Click "Reject"
7. Salesperson notified with reason ✅
```

-----

## 📧 Email Notifications

### Three Email Templates:

#### 1. **Approval Request** (to Managers)

**Trigger:** Salesperson clicks “Request Approval”

**Recipients:** All users in “Discount Manager” group

**Content:**

- Sales order reference
- Customer name
- Order amount
- Discount percentage
- Threshold exceeded
- Direct link to order

#### 2. **Approval Granted** (to Salesperson)

**Trigger:** Manager clicks “Approve”

**Recipient:** Order salesperson

**Content:**

- Approval confirmation
- Approver name
- Order reference
- Next steps

#### 3. **Approval Rejected** (to Salesperson)

**Trigger:** Manager clicks “Reject”

**Recipient:** Order salesperson

**Content:**

- Rejection notification
- Rejection reason
- Manager name
- Suggested actions

-----

## 📦 Dependencies

|Module|Purpose                           |Version|
|------|----------------------------------|-------|
|`sale`|Base sales functionality          |17.0   |
|`mail`|Chatter, activities, notifications|17.0   |

**Automatically Installed:** Both modules are part of standard Odoo installation.

-----

## 🎭 Demo Data

The module includes demo data with 3 sample quotations:

|Order |Customer        |Discount|Threshold|Status            |
|------|----------------|--------|---------|------------------|
|S00001|Deco Addict     |15%     |20%      |No approval needed|
|S00002|Gemini Furniture|25%     |20%      |Waiting approval  |
|S00003|Ready Mat       |30%     |20%      |Approved          |


> **Note:** Demo data only loads if your database was created with “Load demonstration data” enabled.

-----

## 🐛 Troubleshooting

### Common Issues

**Issue:** “Request Approval” button doesn’t appear

- **Solution:**
  - Check discount percentage > threshold
  - Verify order state is “draft”
  - Check approval state is “none”

**Issue:** “No discount managers found” error

- **Solution:** Assign at least one user to “Discount Manager” group

**Issue:** Manager doesn’t see approve/reject buttons

- **Solution:**
  - Verify user has “Discount Manager” group
  - Check order approval state is “waiting”
  - Refresh browser

**Issue:** Emails not sending

- **Solution:**
  - Configure outgoing mail server
  - Check manager email addresses
  - Verify email templates exist

**Issue:** Cannot confirm order with approved discount

- **Solution:**
  - Verify approval_state = “approved”
  - Check if discount was changed after approval
  - Review approval history

### Getting Help

- Check [Odoo Documentation](https://www.odoo.com/documentation/17.0/)
- Review module logs in Odoo (Developer mode → View Logs)
- Open an issue on GitHub
- Contact the author

-----

## 🤝 Contributing

Contributions are welcome! Here’s how you can help:

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
1. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request

### Coding Standards

- Follow [Odoo Development Guidelines](https://www.odoo.com/documentation/17.0/developer/reference/backend/guidelines.html)
- Add comments for complex logic (Arabic comments welcome!)
- Test with multiple companies if adding multi-company features
- Update documentation for new features
- Include demo data for new features

### Ideas for Contributions

- 📊 Add dashboard for approval statistics
- 📱 Mobile app notifications
- 🌍 Multi-level approval (tiered thresholds)
- 📈 Discount analytics and reports
- 🔔 Slack/Teams integration
- ⏱️ Auto-expiry of approvals after X days
- 💬 Comments on approval requests

-----

## 📄 License

This project is licensed under the **GNU Lesser General Public License v3.0** (LGPL-3.0).

See the <LICENSE> file for details.

-----

## 👤 Author

**Mohamed Alaa Elhakim**  
Odoo Developer | Python | ERP Solutions

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohamedalaaelhakim)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:mohamed.alaa918214@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=flat-square&logo=whatsapp&logoColor=white)](https://wa.me/201019272209)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/MohamedAlaaElhakim)

-----

**⭐ If you find this module useful, please give it a star on GitHub!**

-----

## 📝 Changelog

### Version 17.0.2.1.0

- ✅ Fixed approval reset logic when modifying order lines
- ✅ Added discount percentage tracking in approval history
- ✅ Improved email notification performance
- ✅ Enhanced multi-company support
- ✅ Added readonly protection on date fields
- ✅ Fixed currency_id storage in approval history

### Version 17.0.2.0.0

- Initial release for Odoo 17
- Complete discount approval workflow
- Email notifications
- Audit trail
- Multi-company support