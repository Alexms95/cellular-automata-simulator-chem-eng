import { RouterProvider, createRouter } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import {
  QueryClient,
  QueryClientProvider,
  QueryKey,
} from "@tanstack/react-query";
import httpClient from "./lib/httpClient";
import { routeTree } from "./routeTree.gen";

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const defaultQueryFn = async ({ queryKey }: { queryKey: QueryKey }) => {
  const { data } = await httpClient.get(`http://localhost:8000/${queryKey[0]}`);
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
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>
);
