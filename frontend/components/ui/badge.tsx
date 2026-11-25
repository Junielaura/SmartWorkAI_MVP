"use client"

import { ReactNode } from "react"

export interface BadgeProps {
  variant?: "primary" | "secondary" | "success" | "warning" | "danger" | "ai"
  className?: string
}

export function Badge({ variant = "primary", className, children }: BadgeProps) {
  const variants: Record<string, string> = {
    primary: "bg-brand-primary text-primary",
    secondary: "bg-surface-muted/60 text-sidebar-muted",
    success: "bg-success-soft text-success",
    warning: "bg-warning-soft text-warning",
    danger: "bg-danger-soft text-danger",
    ai: "bg-brand-ai text-brand-ai",
  }

  const baseClass = variants[variant] || variants.primary

  return (
    <span
      className={className}
      style={{ ...baseClass.split(" "), background: baseClass.includes("bg-") ? baseClass.match(/bg-\w+[\/-\w]*/)?.[0] || "currentColor" : undefined }}
    >
      {children}
    </span>
  )
}