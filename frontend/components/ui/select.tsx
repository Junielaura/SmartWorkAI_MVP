"use client"

import { ReactNode } from "react"

export interface SelectProps {
  value: string
  onValueChange: (value: string) => void
  children: ReactNode
  className?: string
}

export function Select({ value, onValueChange, children, className }: SelectProps) {
  return (
    <select
      value={value}
      onChange={(e) => onValueChange(e.target.value)}
      className={className}
    >
      {children}
    </select>
  )
}