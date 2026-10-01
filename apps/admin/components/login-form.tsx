"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, LoaderCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { api } from "@/lib/api";

const schema = z.object({
  tenant_slug: z.string().min(2, "Enter your workspace"),
  email: z.email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type LoginValues = z.infer<typeof schema>;

export function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      tenant_slug: "viviz-demo",
      email: "admin@vivizgrowthos.com",
      password: "",
    },
  });

  async function submit(values: LoginValues) {
    try {
      const result = await api.login(values);
      localStorage.setItem("growthos_token", result.access_token);
      onSuccess();
    } catch (error) {
      setError("root", { message: error instanceof Error ? error.message : "Unable to sign in" });
    }
  }

  return (
    <form onSubmit={handleSubmit(submit)} className="login-card" noValidate>
      <div className="brand-mark" aria-hidden="true">V</div>
      <p className="eyebrow">VIVIZ GrowthOS</p>
      <h1>Your business, intelligently assembled.</h1>
      <p className="muted">Sign in to your adaptive growth workspace.</p>

      <label>
        Workspace
        <input {...register("tenant_slug")} autoComplete="organization" />
        {errors.tenant_slug && <span className="field-error">{errors.tenant_slug.message}</span>}
      </label>
      <label>
        Email
        <input {...register("email")} type="email" autoComplete="email" />
        {errors.email && <span className="field-error">{errors.email.message}</span>}
      </label>
      <label>
        Password
        <input {...register("password")} type="password" autoComplete="current-password" />
        {errors.password && <span className="field-error">{errors.password.message}</span>}
      </label>
      {errors.root && <div className="error-banner" role="alert">{errors.root.message}</div>}
      <button className="primary-button" disabled={isSubmitting}>
        {isSubmitting ? <LoaderCircle className="spin" size={18} /> : <>Enter GrowthOS <ArrowRight size={18} /></>}
      </button>
    </form>
  );
}
