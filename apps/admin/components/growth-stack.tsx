"use client";

import { Check, LoaderCircle, Plus, ShieldCheck } from "lucide-react";
import { useState } from "react";

import { api } from "@/lib/api";
import type { Module } from "@/lib/types";

export function GrowthStack({ modules, refresh }: { modules: Module[]; refresh: () => Promise<void> }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function toggle(module: Module) {
    setBusy(module.code);
    setError(null);
    try {
      if (module.enabled) await api.disableModule(module.code);
      else await api.enableModule(module.code);
      await refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update module");
    } finally {
      setBusy(null);
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div><p className="eyebrow">Adaptive platform</p><h1>Your Growth Stack</h1></div>
        <p>Activate only the capabilities this business needs. Required dependencies are handled automatically.</p>
      </div>
      {error && <div className="error-banner" role="alert">{error}</div>}
      <div className="module-grid">
        {modules.map((module) => (
          <article className="module-card" key={module.code}>
            <div className="module-top">
              <span className={`category category-${module.category}`}>{module.category}</span>
              {module.is_core && <span className="core"><ShieldCheck size={15} /> Core</span>}
            </div>
            <h2>{module.name}</h2>
            <p>{module.description}</p>
            <div className="value"><strong>Business value</strong>{module.business_value}</div>
            {module.dependencies.length > 0 && <small>Requires: {module.dependencies.join(", ")}</small>}
            <button
              className={module.enabled ? "module-button enabled" : "module-button"}
              disabled={module.is_core || busy === module.code}
              onClick={() => toggle(module)}
            >
              {busy === module.code ? <LoaderCircle className="spin" size={17} /> : module.enabled ? <><Check size={17} /> Active</> : <><Plus size={17} /> Enable</>}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

