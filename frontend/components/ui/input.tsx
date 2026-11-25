"use client"

import { ReactChangeEvent, ReactHTMLElement, ReactNode } from "react"

export interface InputProps {
  type?: string
  placeholder?: string
  className?: string
  value?: string
  onChange?: (e: ReactChangeEvent<HTMLInputElement>) => void
}

export function Input({ type = "text", placeholder, className, value, onChange }: InputProps) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      className={className}
      value={value}
      onChange={onChange}
    />
  )
}