import { useQuery } from "@tanstack/react-query";
import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/about")({
  component: About,
});

function About() {
  const { isPending, error, data, isFetching } = useQuery({
    queryKey: [""],
  });

  if (isPending) return "Loading...";

  if (error) return "An error has occurred: " + error.message;

  return (
    <div>
      <div>{isFetching ? "Updating..." : ""}</div>
      {JSON.stringify(data)}
    </div>
  );
}
