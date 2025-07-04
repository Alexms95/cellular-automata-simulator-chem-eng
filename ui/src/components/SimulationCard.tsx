import { EditSimulation } from "@/components/editSimulation";
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
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Simulation } from "@/models/simulation";
import { Link } from "@tanstack/react-router";
import { ArrowRightIcon, CopyIcon, Trash2Icon } from "lucide-react";

export function SimulationCard({
  simulation,
  onDelete,
  onCopy,
}: {
  simulation: Simulation;
  onDelete: (id: string) => void;
  onCopy: (id: string) => void;
}) {
  return (
    <Card key={simulation.id}>
      <CardHeader>
        <div className="flex justify-between items-center">
          <Tooltip>
            <TooltipTrigger asChild>
              <div>
                <EditSimulation disabled={false} complete={false} id={simulation.id} />
              </div>
            </TooltipTrigger>
            <TooltipContent>Edit</TooltipContent>
          </Tooltip>
          <CardTitle>{simulation.name}</CardTitle>
          <AlertDialog>
            <Tooltip>
              <AlertDialogTrigger asChild>
                <div>
                  <TooltipTrigger asChild>
                    <Button size="icon" variant="outline" className="w-8 h-8">
                      <Trash2Icon className="m-2 text-red-600" />
                    </Button>
                  </TooltipTrigger>
                </div>
              </AlertDialogTrigger>
              <TooltipContent>Delete</TooltipContent>
            </Tooltip>
            <AlertDialogContent className="dark:text-white">
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
              {`${simulation.gridHeight} x ${simulation.gridLenght} (${simulation.gridLenght * simulation.gridHeight} cells)`}
            </span>
            <span className="block">
              Components:{" "}
              {simulation.ingredients.flatMap((i) => i.name).join(", ")}
            </span>
            <span className="block">
              Created at:{" "}
              {new Date(simulation.created_at + "Z").toLocaleString()}
            </span>
            <span className="block">
              Last updated at:{" "}
              {new Date(simulation.updated_at + "Z").toLocaleString()}
            </span>
          </span>
        </CardDescription>
      </CardHeader>
      <CardFooter className="gap-2">
        <div className="w-1/2">
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                className="w-full h-8 text-xs flex items-center justify-center gap-2"
                variant="outline"
              >
                <CopyIcon className="w-4 h-4" />
                Create a copy
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent className="dark:text-white">
              <AlertDialogHeader>
                <AlertDialogTitle>
                  Do you wish to create a copy of {simulation.name}?
                </AlertDialogTitle>
                <AlertDialogDescription>
                  This action will create a new simulation with the same
                  configuration as {simulation.name}.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => onCopy(simulation.id)}>
                  Create
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
        <Link to={`/simulations/${simulation.id}`} className="w-1/2">
          <Button className="w-full h-8 text-xs flex items-center justify-center gap-2">
            <ArrowRightIcon className="w-4 h-4" />
            Open
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
