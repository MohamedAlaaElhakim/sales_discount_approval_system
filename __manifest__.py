{
    "name": "Sales Discount Approval System",
    "version": "17.0.2.1.0",
    "category": "Sales",
    "summary": "Enhanced discount approval workflow with notifications",
    "description": """
        Sales Discount Approval System
        ===============================
        * Configurable discount threshold
        * Request approval workflow
        * Email notifications
        * Approval history audit trail
        * Manager approval/rejection with reasons
    """,
    "depends": ["sale", "mail"],
    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",
        
        # Configuration
        "views/res_config_settings_views.xml",
        
        # Views
        "views/sale_order_views.xml",
        "views/approval_history_views.xml",
        
        # Wizards
        "wizard/reject_reason_wizard_views.xml",
        
        # Data
        "data/mail_template.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],

    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "auto_install": False,
}
