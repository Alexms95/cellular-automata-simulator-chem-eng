import { ModeToggle } from "@/components/mode-toggle";
import { NewSimulation } from "@/components/newSimulation";
import { SimulationCard } from "@/components/SimulationCard";
import { Skeleton } from "@/components/ui/skeleton";
import httpClient from "@/lib/httpClient";
import { SimulationForm } from "@/lib/utils";
import { Simulation } from "@/models/simulation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";

export const Route = createFileRoute("/simulations/")({
  component: () => <SimulationsList />,
});

function SimulationsList() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery<Simulation[]>({
    queryKey: ["simulations"],
  });

  const deleteSimulation = useMutation({
    mutationFn: (id: string) => httpClient.delete(`/simulations/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulations"] });
    },
  });

  const copySimulation = useMutation({
    mutationFn: (values: SimulationForm) =>
      httpClient.post(`/simulations`, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulations"] });
    },
  });

  const onDelete = async (id: string) => {
    const mutation = deleteSimulation.mutateAsync(id);
    const simulation = data?.find((s) => s.id === id);
    toast.promise(mutation, {
      loading: "Deleting simulation...",
      success: `Simulation ${simulation?.name} deleted!`,
      error: (error) => {
        const message = error.response?.data?.detail;
        return message ?? `Error deleting ${simulation?.name}`;
      },
    });
  };

  const onCopy = async (id: string) => {
    const simulation = data?.find((s) => s.id === id);
    if (!simulation) {
      toast.error("Error copying simulation");
      return;
    }
    const copy = { ...simulation, name: `${simulation.name}_(copy)` };
    const name = simulation.name;
    const mutation = copySimulation.mutateAsync(copy);
    toast.promise(mutation, {
      loading: `Creating a copy of "${name}"...`,
      success: `Created a copy of "${name}"!`,
      error: (error) => {
        const message = error.response?.data?.detail;
        return message ?? `Error creating a copy of ${simulation.name}`;
      },
    });
  };

  return (
    <div className="flex flex-col">
      <div className="fixed top-10 left-4 p-4 z-50">
        <ModeToggle />
      </div>
      <h1 className="scroll-m-20 text-lg font-extrabold tracking-tight lg:text-xl dark:text-zinc-200">
        CELLULAR AUTOMATA SIMULATOR
      </h1>
      <div className="space-y-4 flex flex-col">
        <div className="flex">
          <h2 className="text-lg font-bold w-[54%] text-right dark:text-zinc-200">
            Simulations
          </h2>
          <div className="ml-auto">
            <NewSimulation />
          </div>
        </div>
        {isLoading ? (
          <SimulationsSkeleton />
        ) : (
          <ul className="grid grid-cols-3 xl:grid-cols-4 gap-4 my-2">
            {data
              ?.sort((a, b) => (a.updated_at < b.updated_at ? 1 : -1))
              .map((simulation) => (
                <SimulationCard
                  key={simulation.id}
                  simulation={simulation}
                  onDelete={onDelete}
                  onCopy={onCopy}
                />
              ))}
          </ul>
        )}
      </div>
    </div>
  );
}

const SimulationsSkeleton = () => {
  return (
    <ul className="grid grid-cols-4">
      {Array.from({ length: 8 }, (_, i) => (
        <div key={i} className="flex flex-col space-y-3 mx-auto my-4">
          <Skeleton className="h-[100px] w-[250px] rounded-xl" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        </div>
      ))}
    </ul>
  );
};
