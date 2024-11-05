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
import { ApiResult } from "@/models/apiResult";
import { Simulation } from "@/models/simulation";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { CopyIcon, Trash2Icon } from "lucide-react";

export const Route = createFileRoute("/simulations/")({
  component: () => <SimulationsList />,
});

function SimulationsList() {
  const { data, isLoading } = useQuery<ApiResult<Simulation[]>>({
    queryKey: ["simulations"],
  });

  const simulations = data?.results;

  return (
    <div className="flex flex-col">
      <h1 className="scroll-m-20 text-lg font-extrabold tracking-tight lg:text-xl">
        CELLULAR AUTOMATA SIMULATOR
      </h1>
      <div className="space-y-4 flex flex-col">
        <NewSimulation />
        <h2 className="text-lg font-bold">Simulations</h2>
        {isLoading ? (
          <SimulationsSkeleton />
        ) : (
          <ul className="grid grid-cols-4 xl:grid-cols-5">
            {simulations?.map((simulation) => (
              <Card key={simulation.id} className="w-[250px] mx-auto my-2">
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="outline" size="icon">
                          <CopyIcon className="m-2" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Create a copy</TooltipContent>
                    </Tooltip>
                    <CardTitle>{simulation.name}</CardTitle>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button size="icon" variant="outline">
                          <Trash2Icon className="m-2 text-red-600" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Delete</TooltipContent>
                    </Tooltip>
                  </div>
                  <CardDescription>
                    Deploy your new project in one-click.
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
