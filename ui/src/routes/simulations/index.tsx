import { NewSimulation } from "@/components/newSimulation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import httpClient from "@/lib/httpClient";
import { Simulation } from "@/models/simulation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { CopyIcon, Trash2Icon } from "lucide-react";
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
    mutationFn: (values: NewSimulation) =>
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
      error: "Error deleting simulation",
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
      error: `Error copying ${name}`,
    });
  };

  return (
    <div className="flex flex-col">
      <h1 className="scroll-m-20 text-lg font-extrabold tracking-tight lg:text-xl">
        CELLULAR AUTOMATA SIMULATOR
      </h1>
      <div className="space-y-4 flex flex-col">
        <div className="flex">
          <h2 className="text-lg font-bold w-[54%] text-right">Simulations</h2>
          <div className="ml-auto">
            <NewSimulation />
          </div>
        </div>
        {isLoading ? (
          <SimulationsSkeleton />
        ) : (
          <ul className="grid grid-cols-4 xl:grid-cols-5">
            {data?.map((simulation) => (
              <Card key={simulation.id} className="w-[250px] mx-auto my-2">
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          onClick={() => onCopy(simulation.id)}
                          variant="outline"
                          size="icon"
                        >
                          <CopyIcon className="m-2" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Create a copy</TooltipContent>
                    </Tooltip>
                    <CardTitle>{simulation.name}</CardTitle>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          onClick={() => onDelete(simulation.id)}
                          size="icon"
                          variant="outline"
                        >
                          <Trash2Icon className="m-2 text-red-600" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Delete</TooltipContent>
                    </Tooltip>
                  </div>
                  <CardDescription>
                    <span>{simulation.iterationsNumber} iterations</span>
                    <span>
                      Grid Size:{" "}
                      {`${simulation.gridSize} x ${simulation.gridSize}`}
                    </span>
                    <span>
                      Ingredients:{" "}
                      {simulation.ingredients.flatMap((i) => i.name).join(", ")}
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardFooter>
                  <Link to={`/simulations/${simulation.id}`} className="w-full">
                    <Button className="w-full">Open</Button>
                  </Link>
                </CardFooter>
              </Card>
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
