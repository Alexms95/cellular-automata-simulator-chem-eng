import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/simulations/')({
  component: () => <div>Hello /simulations/!</div>,
})
