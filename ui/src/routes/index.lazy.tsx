import App from "@/App";
import { TooltipProvider } from "@radix-ui/react-tooltip";
import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/")({
  component: Index,
});

function Index() {
  return (
    <TooltipProvider>
      <App />
    </TooltipProvider>
  );
}
