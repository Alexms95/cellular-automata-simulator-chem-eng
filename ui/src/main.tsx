import { scan, getReport } from "react-scan";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Toaster } from "sonner";
import "./index.css";

import {
  QueryClient,
  QueryClientProvider,
  QueryKey,
} from "@tanstack/react-query";
import { Spinner } from "./components/ui/spinner";
import { TooltipProvider } from "./components/ui/tooltip";
import httpClient from "./lib/httpClient";
import { routeTree } from "./routeTree.gen";

if (typeof window !== "undefined") {
  scan({
    enabled: false,
    log: true,// logs render info to console (default: false)
  });
  const a = getReport();
  console.log(a);
}

const router = createRouter({
  routeTree,
  defaultPendingComponent: () => <Spinner />,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const defaultQueryFn = async ({ queryKey }: { queryKey: QueryKey }) => {
  const path = queryKey.reduce((acc, cur) => 
    `${acc}/${cur}`
  );

  const { data } = await httpClient.get(`http://localhost:8000/${path}`);
  return data;
};
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      queryFn: defaultQueryFn,
      refetchOnWindowFocus: false,
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Toaster duration={3000} expand={true} position="top-right" richColors />
      <TooltipProvider delayDuration={300}>
        <RouterProvider router={router} />
      </TooltipProvider>
    </QueryClientProvider>
  </StrictMode>
);
