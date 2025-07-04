import { RouterProvider, createRouter } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { getReport, scan } from "react-scan";
import { Toaster } from "sonner";
import "./index.css";

import { QueryClientProvider } from "@tanstack/react-query";
import { Spinner } from "./components/ui/spinner";
import { TooltipProvider } from "./components/ui/tooltip";
import { queryClient } from "./queryClient";
import { routeTree } from "./routeTree.gen";
import { ThemeProvider } from "./components/theme-provider";

if (typeof window !== "undefined") {
  scan({
    enabled: false,
    log: true, // logs render info to console (default: false)
  });
  const a = getReport();
  console.log(a);
}

const router = createRouter({
  routeTree,
  defaultPendingComponent: () => <Spinner />,
  defaultErrorComponent: ({ error }) => {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-2xl font-bold">Error</h1>
        <p className="text-red-500">{error.message}</p>
      </div>
    );
  },
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <Toaster
          duration={2000}
          expand={true}
          position="top-right"
          richColors
        />
        <TooltipProvider delayDuration={300}>
          <RouterProvider router={router} />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
);
