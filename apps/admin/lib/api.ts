import type { CurrentUser, Module, NavigationItem } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window === "undefined" ? null : localStorage.getItem("growthos_token");
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(payload?.detail ?? "The request could not be completed", response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  login: (body: { tenant_slug: string; email: string; password: string }) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  me: () => request<CurrentUser>("/auth/me"),
  navigation: () => request<NavigationItem[]>("/navigation"),
  modules: () => request<Module[]>("/modules"),
  enableModule: (code: string) =>
    request<{ enabled: string[]; dependencies_activated: string[] }>(`/modules/${code}/enable`, {
      method: "POST",
      body: JSON.stringify({ source: "manual", activate_dependencies: true }),
    }),
  disableModule: (code: string) => request<void>(`/modules/${code}/disable`, { method: "POST" }),
};

