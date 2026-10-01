from typing import Any

MODULE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "code": "core",
        "name": "Core Platform",
        "category": "platform",
        "description": "Tenant, identity, settings, audit, and platform navigation.",
        "business_value": "Provides the secure operating foundation for GrowthOS.",
        "is_core": True,
        "permissions": ["dashboard.view", "settings.view", "modules.manage"],
        "navigation": [
            {
                "label": "Dashboard",
                "href": "/dashboard",
                "icon": "LayoutDashboard",
                "permission": "dashboard.view",
            },
            {
                "label": "Growth Stack",
                "href": "/growth-stack",
                "icon": "Blocks",
                "permission": "modules.manage",
            },
            {
                "label": "Settings",
                "href": "/settings",
                "icon": "Settings",
                "permission": "settings.view",
            },
        ],
    },
    {
        "code": "leads",
        "name": "Lead CRM",
        "category": "crm",
        "description": "Capture, qualify, assign, and track business enquiries.",
        "business_value": "Centralizes enquiries and prevents missed follow-ups.",
        "permissions": ["leads.view", "leads.create", "leads.update", "leads.delete"],
        "navigation": [
            {"label": "Leads", "href": "/leads", "icon": "Users", "permission": "leads.view"}
        ],
    },
    {
        "code": "contacts",
        "name": "Contacts",
        "category": "crm",
        "description": "Maintain a reusable customer and prospect directory.",
        "business_value": "Creates a reliable customer database.",
        "permissions": ["contacts.view", "contacts.create", "contacts.update"],
        "navigation": [
            {
                "label": "Contacts",
                "href": "/contacts",
                "icon": "Contact",
                "permission": "contacts.view",
            }
        ],
    },
    {
        "code": "appointments",
        "name": "Appointments",
        "category": "booking",
        "description": "Configurable booking for appointments, demos, and consultations.",
        "business_value": "Reduces manual scheduling and missed appointments.",
        "permissions": ["appointments.view", "appointments.manage"],
        "navigation": [
            {
                "label": "Appointments",
                "href": "/appointments",
                "icon": "CalendarDays",
                "permission": "appointments.view",
            }
        ],
    },
    {
        "code": "whatsapp",
        "name": "WhatsApp",
        "category": "communication",
        "description": "Official WhatsApp Business Platform integration.",
        "business_value": "Handles customer conversations on a preferred channel.",
        "permissions": ["whatsapp.view", "whatsapp.send", "whatsapp.configure"],
        "navigation": [
            {
                "label": "WhatsApp",
                "href": "/whatsapp",
                "icon": "MessageCircle",
                "permission": "whatsapp.view",
            }
        ],
    },
    {
        "code": "workflow_engine",
        "name": "Workflow Automation",
        "category": "automation",
        "description": "Trigger, condition, and action based business workflows.",
        "business_value": "Automates repetitive follow-up and operational tasks.",
        "permissions": ["workflows.view", "workflows.manage"],
        "navigation": [
            {
                "label": "Automation",
                "href": "/automation",
                "icon": "Workflow",
                "permission": "workflows.view",
            }
        ],
        "dependencies": ["internal_notifications"],
    },
    {
        "code": "internal_notifications",
        "name": "Internal Notifications",
        "category": "communication",
        "description": "In-product notification delivery framework.",
        "business_value": "Keeps teams informed about important events.",
        "permissions": ["notifications.view"],
        "navigation": [],
    },
    {
        "code": "site_visit_booking",
        "name": "Site Visit Booking",
        "category": "real_estate",
        "description": "Schedule and manage real-estate site visits.",
        "business_value": "Converts property interest into organized visits.",
        "permissions": ["site_visits.view", "site_visits.manage"],
        "navigation": [
            {
                "label": "Site Visits",
                "href": "/site-visits",
                "icon": "MapPin",
                "permission": "site_visits.view",
            }
        ],
        "dependencies": ["appointments", "property_listing"],
    },
    {
        "code": "property_listing",
        "name": "Property Listings",
        "category": "real_estate",
        "description": "Manage property inventory and public listings.",
        "business_value": "Turns property inventory into searchable opportunities.",
        "permissions": [
            "properties.view",
            "properties.create",
            "properties.update",
            "properties.delete",
        ],
        "navigation": [
            {
                "label": "Properties",
                "href": "/properties",
                "icon": "Building2",
                "permission": "properties.view",
            }
        ],
    },
    {
        "code": "analytics",
        "name": "Analytics",
        "category": "analytics",
        "description": "Business and module-aware performance reporting.",
        "business_value": "Makes growth decisions measurable.",
        "permissions": ["analytics.view"],
        "navigation": [
            {
                "label": "Analytics",
                "href": "/analytics",
                "icon": "ChartNoAxesCombined",
                "permission": "analytics.view",
            }
        ],
    },
    {
        "code": "product_catalog",
        "name": "Product Catalog",
        "category": "ecommerce",
        "description": "Structured products, categories, pricing, and availability.",
        "business_value": "Creates the product foundation for online discovery and sales.",
        "permissions": ["products.view", "products.manage"],
        "navigation": [
            {
                "label": "Products",
                "href": "/products",
                "icon": "PackageSearch",
                "permission": "products.view",
            }
        ],
    },
    {
        "code": "cart",
        "name": "Shopping Cart",
        "category": "ecommerce",
        "description": "Persistent customer shopping baskets.",
        "business_value": "Lets customers prepare an online purchase.",
        "permissions": ["cart.manage"],
        "navigation": [],
        "dependencies": ["product_catalog"],
    },
    {
        "code": "orders",
        "name": "Orders",
        "category": "ecommerce",
        "description": "Order capture and fulfilment tracking.",
        "business_value": "Provides an operational record of online sales.",
        "permissions": ["orders.view", "orders.manage"],
        "navigation": [
            {
                "label": "Orders",
                "href": "/orders",
                "icon": "ShoppingBag",
                "permission": "orders.view",
            }
        ],
        "dependencies": ["product_catalog", "cart"],
    },
]
