"use client";

import { useCallback, useEffect, useState } from "react";

import { AdaptiveSidebar } from "@/components/adaptive-sidebar";
import { GrowthStack } from "@/components/growth-stack";
import { LoginForm } from "@/components/login-form";
import { ApiError, api } from "@/lib/api";
import type { CurrentUser, Module, NavigationItem } from "@/lib/types";

export function Workspace() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState("/dashboard");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [navigation, setNavigation] = useState<NavigationItem[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [me, nav, catalog] = await Promise.all([api.me(), api.navigation(), api.modules()]);
      setUser(me);
      setNavigation(nav);
      setModules(catalog);
      setAuthenticated(true);
      setError(null);
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        localStorage.removeItem("growthos_token");
        setAuthenticated(false);
      } else {
        setError(cause instanceof Error ? cause.message : "GrowthOS is unavailable");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => void load());
  }, [load]);

  if (loading) return <main className="center"><div className="loader" aria-label="Loading" /></main>;
  if (!authenticated) return <main className="login-shell"><LoginForm onSuccess={() => void load()} /></main>;

  return (
    <div className="app-shell">
      <AdaptiveSidebar items={navigation} active={active} onNavigate={setActive} />
      <main className="workspace-main">
        <header className="topbar">
          <div><span className="status-dot" /> Adaptive workspace</div>
          <div className="user-chip"><span>{user?.full_name.slice(0, 1)}</span><div><strong>{user?.full_name}</strong><small>{user?.email}</small></div></div>
        </header>
        <div className="content">
          {error && <div className="error-banner" role="alert">{error}</div>}
          {active === "/growth-stack" ? <GrowthStack modules={modules} refresh={load} /> : (
            <section>
              <div className="page-heading"><div><p className="eyebrow">Good morning</p><h1>Growth overview</h1></div><p>Your dashboard will adapt as modules and business signals become available.</p></div>
              <div className="metric-grid">
                <article><span>Active modules</span><strong>{modules.filter((module) => module.enabled).length}</strong><small>of {modules.length} available</small></article>
                <article><span>Workspace readiness</span><strong>{modules.some((module) => module.enabled && !module.is_core) ? "Growing" : "Foundation"}</strong><small>Next: complete business assessment</small></article>
                <article><span>Platform status</span><strong className="healthy">Healthy</strong><small>Entitlements enforced</small></article>
              </div>
              <div className="empty-state"><div className="brand-mark">↗</div><h2>Your dashboard grows with you</h2><p>Enable modules in Growth Stack to add relevant business widgets—without clutter from features you do not use.</p><button className="primary-button compact" onClick={() => setActive("/growth-stack")}>Configure Growth Stack</button></div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
