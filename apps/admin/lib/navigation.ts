import type { NavigationItem } from "./types";

export function visibleNavigation(items: NavigationItem[], permissions: string[]) {
  const granted = new Set(permissions);
  return items.filter((item) => !item.permission || granted.has(item.permission));
}

