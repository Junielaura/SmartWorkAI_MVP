"use client"

import { ReactNode } from "react"

export interface CardProps {
  className?: string
  children: ReactNode
}

export function Card({ className, children }: CardProps) {
  return (
    <div className={className || "sw-card"}>{children}</div>
  )
}