import { describe, expect, it } from "vitest";

import { visibleNavigation } from "./navigation";

describe("adaptive navigation", () => {
  it("further restricts enabled module links by permission", () => {
    const result = visibleNavigation(
      [
        { label: "Leads", href: "/leads", icon: "Users", permission: "leads.view", module_code: "leads" },
        { label: "Settings", href: "/settings", icon: "Settings", permission: "settings.view", module_code: "core" },
      ],
      ["settings.view"],
    );
    expect(result.map((item) => item.label)).toEqual(["Settings"]);
  });
});

