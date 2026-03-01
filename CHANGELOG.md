# CHANGELOG - Sales Discount Approval System

## Version 17.0.2.1.0 - Bug Fixes (2026-03-01)

### 🐛 Critical Bug Fixes

#### 1. XML Views - Invisible Attributes
**File:** `views/sale_order_views.xml`
- **Fixed:** Lines 24, 31, 38, 59
- **Issue:** Using deprecated `== False` syntax for invisible attributes
- **Solution:** Changed to `not field_name` syntax for Odoo 17 compatibility
- **Impact:** Buttons will now show/hide correctly

**Before:**
```xml
invisible="show_request_approval == False"
invisible="approver_id == False"
```

**After:**
```xml
invisible="not show_request_approval"
invisible="not approver_id"
```

---

#### 2. Sale Order Model - Onchange Logic
**File:** `models/sale_order.py`
- **Fixed:** Lines 95-101
- **Issue:** 
  - `@api.onchange` doesn't work properly with `order_line.discount`
  - No warning shown to user when approval is reset
  - Changes weren't persisted properly
- **Solution:** 
  - Fixed onchange to work with `order_line` only
  - Added warning message
  - Added `write()` override for proper persistence
- **Impact:** Users will be notified when discount changes reset approval

**Added:**
```python
def write(self, vals):
    """Override write to handle discount changes after approval"""
    # Properly handles discount changes and resets approval
    # Posts notification message in chatter
```

---

#### 3. Email Notifications - Not Sending
**File:** `models/sale_order.py`
- **Fixed:** `_notify_managers()` method (lines 246-265)
- **Issue:**
  - Only first manager was notified
  - No actual emails were sent (only activities created)
  - No error handling if no managers exist
- **Solution:**
  - Create activities for ALL managers
  - Send actual email notifications using templates
  - Added error handling for missing managers
- **Impact:** All managers will receive email notifications

**Key Changes:**
```python
# Before: Activity for first manager only
user_id=managers[0].id

# After: Activity and email for ALL managers
for manager in managers:
    self.activity_schedule(...)
    template.send_mail(...)
```

---

#### 4. Email Notifications - Salesperson
**File:** `models/sale_order.py`
- **Fixed:** `_notify_salesperson()` method (lines 267-282)
- **Issue:** Only chatter message, no email sent
- **Solution:** Added email template sending
- **Impact:** Salespeople will receive email notifications

---

#### 5. Mail Templates - Email Recipients
**File:** `data/mail_template.xml`
- **Fixed:** Line 10 - `email_template_approval_request`
- **Issue:** Email sent to company email instead of managers
- **Solution:** Removed `email_to` field, emails sent programmatically
- **Impact:** Correct recipients will receive emails

---

#### 6. Mail Templates - Rejection Reason
**File:** `data/mail_template.xml`
- **Fixed:** Line 140 - `email_template_approval_rejected`
- **Issue:** Using `[0]` might not get the latest rejection
- **Solution:** Filter rejected records and sort by date
- **Impact:** Correct rejection reason will be shown

**Before:**
```jinja
{{ object.approval_history_ids[0].reason }}
```

**After:**
```jinja
{% set rejected_records = object.approval_history_ids.filtered(lambda h: h.action == 'rejected').sorted(lambda r: r.date, reverse=True) %}
{{ rejected_records[0].reason if rejected_records else 'No reason provided' }}
```

---

#### 7. Approval History - Create Method
**File:** `models/approval_history.py`
- **Fixed:** Lines 77-84
- **Issue:** Setting `discount_percentage` after create (extra SQL queries)
- **Solution:** Set value in `vals` before create
- **Impact:** Better performance, fewer database queries

---

#### 8. Security - Access Rights
**File:** `security/ir.model.access.csv`
- **Fixed:** Added lines 6-7
- **Issue:** Missing access rights for `res.company`
- **Solution:** Added read/write access for discount users/managers
- **Impact:** No permission errors when accessing settings

---

### ✅ Testing Checklist

After applying these fixes, test the following scenarios:

1. **Button Visibility:**
   - [ ] Request Approval button appears when discount > threshold
   - [ ] Approve/Reject buttons appear for managers only
   - [ ] Approver field shows only when set

2. **Email Notifications:**
   - [ ] Managers receive email when approval requested
   - [ ] Salesperson receives email when approved
   - [ ] Salesperson receives email when rejected
   - [ ] All managers receive notifications (not just first one)

3. **Discount Changes:**
   - [ ] Warning appears when discount changed after approval
   - [ ] Approval state resets to "none"
   - [ ] Approver field is cleared
   - [ ] Message posted in chatter

4. **Approval History:**
   - [ ] Discount percentage saved automatically
   - [ ] Latest rejection reason shown in email
   - [ ] Records cannot be deleted

5. **Settings:**
   - [ ] Users can view discount threshold
   - [ ] Managers can modify threshold
   - [ ] No permission errors

---

### 📊 Impact Analysis

| Component | Severity | Fixed | Impact |
|-----------|----------|-------|--------|
| Button Visibility | HIGH | ✅ | Critical UI issue |
| Email Notifications | HIGH | ✅ | Core functionality |
| Discount Change Logic | MEDIUM | ✅ | User experience |
| Performance | MEDIUM | ✅ | Database efficiency |
| Access Rights | LOW | ✅ | Permission errors |

---

### 🔄 Migration Notes

**Upgrading from 17.0.2.0.0 to 17.0.2.1.0:**

1. Backup your database
2. Update module code
3. Update the module in Odoo: `Apps > Sales Discount Approval System > Upgrade`
4. Test in staging environment first
5. Clear browser cache
6. Test all workflows

**No data migration required** - these are code-only fixes.

---

### 📝 Known Limitations

The following items are NOT included in this fix (future enhancements):

1. **Approval Expiry:** Approvals don't expire
2. **Approval Delegation:** No delegation mechanism
3. **Multi-level Approval:** Single level approval only
4. **Approval by Discount Amount:** All managers can approve any discount
5. **Unit Tests:** No automated tests included

---

### 🆘 Support

If you encounter any issues after applying these fixes:

1. Check Odoo server logs for errors
2. Verify all managers have email addresses configured
3. Check mail server configuration
4. Ensure all required modules are installed (sale, mail)
5. Clear browser cache and refresh

---

### 👨‍💻 Technical Details

**Lines of Code Changed:** 127 lines
**Files Modified:** 5 files
**New Files:** 0
**Deleted Files:** 0
**Breaking Changes:** None

**Modified Files:**
1. `views/sale_order_views.xml` - 4 changes
2. `models/sale_order.py` - 3 major methods fixed
3. `models/approval_history.py` - 1 method optimized
4. `data/mail_template.xml` - 2 templates fixed
5. `security/ir.model.access.csv` - 2 entries added

---

### ✨ What's Next?

**Recommended Future Enhancements:**

1. Add approval expiry (e.g., 7 days)
2. Add multi-level approval based on discount amount
3. Add approval delegation when manager is absent
4. Add unit tests for critical methods
5. Add dashboard for approval statistics
6. Add email digest for pending approvals

---

**Last Updated:** 2026-03-01  
**Version:** 17.0.2.1.0  
**Odoo Compatibility:** 17.0  
**Module:** sales_discount_approval_system
