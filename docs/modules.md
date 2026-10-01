# Module Framework

Each catalog entry defines a stable code, category, description, business value, core/billable flags, minimum plan, version, configuration schema, permissions, and navigation metadata.

Activation resolves required dependencies in topological order. Activation can be rejected when dependency consent is not supplied. Deactivation is blocked while another enabled module depends on the target. Core modules cannot be disabled.

Initial catalog coverage includes core, leads, contacts, appointments, WhatsApp, workflow notifications, real-estate listings/site visits, analytics, and the ecommerce product/cart/order foundation. Catalog presence does not imply that the feature’s business CRUD is implemented; consult `IMPLEMENTATION_STATUS.md`.

