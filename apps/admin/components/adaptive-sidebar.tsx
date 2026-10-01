"use client";

import {
  BarChart3,
  Blocks,
  Building2,
  CalendarDays,
  ChartNoAxesCombined,
  Contact,
  LayoutDashboard,
  MapPin,
  MessageCircle,
  Settings,
  Users,
  Workflow,
} from "lucide-react";

import type { NavigationItem } from "@/lib/types";

const icons = {
  BarChart3, Blocks, Building2, CalendarDays, ChartNoAxesCombined, Contact,
  LayoutDashboard, MapPin, MessageCircle, Settings, Users, Workflow,
};

export function AdaptiveSidebar({
  items,
  active,
  onNavigate,
}: {
  items: NavigationItem[];
  active: string;
  onNavigate: (href: string) => void;
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand"><span>V</span><strong>GrowthOS</strong></div>
      <nav aria-label="Workspace navigation">
        {items.map((item) => {
          const Icon = icons[item.icon as keyof typeof icons] ?? Blocks;
          return (
            <button
              key={`${item.module_code}-${item.href}`}
              className={active === item.href ? "nav-item active" : "nav-item"}
              onClick={() => onNavigate(item.href)}
            >
              <Icon size={19} /> <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="sidebar-foot"><span className="status-dot" /> Platform operational</div>
    </aside>
  );
}

