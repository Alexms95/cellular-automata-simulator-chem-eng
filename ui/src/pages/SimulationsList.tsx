import { NewSimulation } from "@/components/newSimulation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ApiResult } from "@/models/apiResult";
import { Simulation } from "@/models/simulation";
import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { PenIcon, PlusCircle, Trash2Icon } from "lucide-react";

export const SimulationsList = () => {
  const { data, isLoading } = useQuery<ApiResult<Simulation[]>>({
    queryKey: ["simulations"],
  });

  const simulations = data?.results;

  return (
    <div className="space-y-4 w-full flex flex-col">
      <Dialog>
        <DialogTrigger asChild>
          <Button className="self-end mr-4">
            <PlusCircle className="mr-2"></PlusCircle>New Simulation
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>New Simulation</DialogTitle>
            <DialogDescription>
              Create a new simulation. Save it when you are done.
            </DialogDescription>
          </DialogHeader>
          <NewSimulation />
          <DialogFooter>
            <DialogClose asChild>
              <Button
                type="submit"
                form="new-simulation-form"
                className="w-full"
              >
                Save
              </Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <h2 className="text-lg font-bold">Simulations</h2>
      {isLoading ? (
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
                    <TooltipContent>Edit</TooltipContent>
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
                <Link to="/about" className="w-full">
                  <Button className="w-full">Open</Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </ul>
      )}
    </div>
  );
};
