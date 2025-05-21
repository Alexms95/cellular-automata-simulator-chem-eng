import { QueryClient, QueryKey } from "@tanstack/react-query";
import httpClient from "./lib/httpClient";

const defaultQueryFn = async ({ queryKey }: { queryKey: QueryKey }) => {
  const path = queryKey.reduce((acc, cur) => `${acc}/${cur}`);

  const { data } = await httpClient.get(`http://localhost:8000/${path}`);
  return data;
};

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      queryFn: defaultQueryFn,
      refetchOnWindowFocus: false,
    },
  },
});
