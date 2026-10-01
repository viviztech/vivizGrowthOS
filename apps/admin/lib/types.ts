export type NavigationItem = {
  label: string;
  href: string;
  icon: string;
  permission?: string;
  module_code?: string;
};

export type Module = {
  code: string;
  name: string;
  category: string;
  description: string;
  business_value: string;
  is_core: boolean;
  is_billable: boolean;
  version: string;
  enabled: boolean;
  configured: boolean;
  dependencies: string[];
};

export type CurrentUser = {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  permissions: string[];
};

