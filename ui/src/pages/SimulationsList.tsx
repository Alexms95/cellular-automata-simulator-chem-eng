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
} from "@radix-ui/react-tooltip";
import { PenIcon, Trash2Icon } from "lucide-react";
import { useState } from "react";

export const SimulationsList = () => {
  const simulations = Array.from({ length: 6 }, (_, i) => ({
    id: i + 1,
    name: `Simulation ${i + 1}`,
  }));

  const [isLoading, setIsLoading] = useState(true);

  setTimeout(() => {
    setIsLoading(false);
  }, 2000);

  return (
    <div className="space-y-4 w-full flex flex-col">
      <h2 className="text-lg font-bold">Simulations</h2>
      {isLoading ? (
        <ul className="grid grid-cols-4">
          {Array.from({ length: 8 }, () => (
            <div className="flex flex-col space-y-3 mx-auto my-4">
              <Skeleton className="h-[100px] w-[250px] rounded-xl" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-[200px]" />
              </div>
            </div>
          ))}
        </ul>
      ) : (
        <ul className="grid grid-cols-4">
          {simulations?.map((simulation) => (
            <Card key={simulation.id} className="w-[250px] mx-auto my-2">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="outline" size="icon">
                        <PenIcon className="m-2" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p className="text-sm bg-zinc-600 rounded border-zinc-300 border px-2 py-1 mb-2 text-zinc-100">
                        Edit
                      </p>
                    </TooltipContent>
                  </Tooltip>
                  <CardTitle>{simulation.name}</CardTitle>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant="outline">
                        <Trash2Icon className="m-2 text-red-600" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p className="text-sm bg-zinc-600 rounded border-zinc-300 border px-2 py-1 mb-2 text-zinc-100">
                        Delete
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <CardDescription>
                  Deploy your new project in one-click.
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Button className="w-full">Open</Button>
              </CardFooter>
            </Card>
          ))}
        </ul>
      )}
    </div>
  );
};
