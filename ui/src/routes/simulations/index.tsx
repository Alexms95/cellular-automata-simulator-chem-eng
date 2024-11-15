import { EditSimulation } from "@/components/editSimulation";
import { NewSimulation } from "@/components/newSimulation";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogActionDestructive,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
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
import { SimulationForm } from "@/lib/utils";
import { Simulation } from "@/models/simulation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Trash2Icon } from "lucide-react";
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
          <ul className="grid grid-cols-3 xl:grid-cols-4 gap-4 my-2">
            {data?.sort((a, b) => a.updated_at < b.updated_at ? 1 : -1).map((simulation) => (
              <Card key={simulation.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="outline"
                          size="icon"
                          className="w-8 h-8"
                        >
                          <EditSimulation id={simulation.id} />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Edit</TooltipContent>
                    </Tooltip>
                    <CardTitle className="text-sm">{simulation.name}</CardTitle>
                    <AlertDialog>
                      <Tooltip>
                        <AlertDialogTrigger asChild>
                          <div>
                            <TooltipTrigger asChild>
                              <Button
                                size="icon"
                                variant="outline"
                                className="w-8 h-8"
                              >
                                <Trash2Icon className="m-2 text-red-600" />
                              </Button>
                            </TooltipTrigger>
                          </div>
                        </AlertDialogTrigger>
                        <TooltipContent>Delete</TooltipContent>
                      </Tooltip>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Are you sure you want to delete {simulation.name}?
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogActionDestructive
                            onClick={() => onDelete(simulation.id)}
                          >
                            Yes, Delete
                          </AlertDialogActionDestructive>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                  <CardDescription className="text-xs">
                    <span>
                      <span className="block">
                        {simulation.iterationsNumber} iterations
                      </span>
                      <span className="block">
                        Grid Dimensions:{" "}
                        {`${simulation.gridLenght} x ${simulation.gridHeight} (${simulation.gridLenght * simulation.gridHeight} cells)`}
                      </span>
                      <span className="block">
                        Components:{" "}
                        {simulation.ingredients
                          .flatMap((i) => i.name)
                          .join(", ")}
                      </span>
                        <span className="block">
                          Created at: {new Date(simulation.created_at + 'Z').toLocaleString()}
                        </span>
                        <span className="block">
                          Last updated at: {new Date(simulation.updated_at + 'Z').toLocaleString()}
                        </span>
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardFooter className="gap-2">
                  <div className="w-1/2">
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          className="w-full h-8 text-xs"
                          variant="outline"
                        >
                          Create a copy
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Do you wish to create a copy of {simulation.name}?
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            This action will create a new simulation with the
                            same configuration as {simulation.name}.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => onCopy(simulation.id)}
                          >
                            Create
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                  <Link to={`/simulations/${simulation.id}`} className="w-1/2">
                    <Button className="w-full h-8 text-xs">Open</Button>
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
