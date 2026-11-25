"use client"

import { ReactNode } from "react"

export interface ButtonProps {
  variant?: "primary" | "secondary" | "ai" | "outline"
  className?: string
  children: ReactNode
  onClick?: () => void
  disabled?: boolean
}

export function Button({ variant = "primary", className, children, onClick, disabled }: ButtonProps) {
  const variantClasses: Record<string, string> = {
    primary: "sw-btn-primary",
    secondary: "sw-btn-secondary",
    ai: "sw-btn-ai",
    outline: "sw-btn-outline",
  }

  return (
    <button
      className={`${variantClasses[variant] || variantClasses.primary} ${className} w-full`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}