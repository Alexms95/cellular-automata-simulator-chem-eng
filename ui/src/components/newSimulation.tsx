import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { PlusCircle, TrashIcon } from "lucide-react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Label } from "./ui/label";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";

const formSchema = z.object({
  simulationName: z.string().min(3, {
    message: "It must be at least 3 characters.",
  }),
  iterationsNumber: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
  gridDimension: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
  ingredients: z.array(
    z.object({
      name: z.string().min(1, {
        message: "It must be at least 1 character.",
      }),
      color: z.string().min(7, {
        message: "It must be a color.",
      }),
    })
  ),
});

type NewSimulationForm = z.infer<typeof formSchema>;

export const NewSimulation = () => {
  const form = useForm<NewSimulationForm>({
    resolver: zodResolver(formSchema),
    mode: "onTouched",
    defaultValues: {
      simulationName: "",
      iterationsNumber: 1,
      gridDimension: 1,
      ingredients: [{ name: "A", color: "fff" }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "ingredients",
  });

  const onSubmit = (values: NewSimulationForm) => {
    console.log(values);
  };

  return (
    <Form {...form}>
      <Dialog>
        <DialogTrigger asChild>
          <Button className="self-end mr-4">
            <PlusCircle className="mr-2"></PlusCircle>New Simulation
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[80%] overflow-y-scroll max-h-[90%]">
          <DialogHeader>
            <DialogTitle>New Simulation</DialogTitle>
            <DialogDescription>
              Create a new simulation. Save it when you are done.
            </DialogDescription>
          </DialogHeader>
          <div className="grid w-full max-w-sm items-center gap-2">
            <Label htmlFor="file">Import a file</Label>
            <Input id="file" type="file" />
          </div>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="space-y-4 flex flex-col"
            id="new-simulation-form"
          >
            <div className="flex space-x-4">
              <div className="w-1/3">
                <FormField
                  control={form.control}
                  name="simulationName"
                  render={({ field }) => (
                    <FormItem className="flex flex-col items-start">
                      <FormLabel>Simulation Name</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Give a name for your simulation"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        Choose an easy-to-find name.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <div className="w-1/3">
                <FormField
                  control={form.control}
                  name="iterationsNumber"
                  render={({ field }) => (
                    <FormItem className="flex flex-col items-start">
                      <FormLabel>Number of Iterations</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Choose the number of iterations"
                          type="number"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        How many iterations will be performed.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <div className="w-1/3">
                <FormField
                  control={form.control}
                  name="gridDimension"
                  render={({ field }) => (
                    <FormItem className="flex flex-col items-start">
                      <FormLabel>Grid Dimension</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Choose the grid dimension"
                          type="number"
                          {...field}
                        />
                      </FormControl>
                      {!form.formState.errors.gridDimension && (
                        <FormDescription>
                          A grid of {form.getValues("gridDimension")} x{" "}
                          {form.getValues("gridDimension")} will be created.
                        </FormDescription>
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="flex space-x-4">
                  <p className="w-1/8 text-sm font-semibold mt-8">
                    Ingredient {String.fromCharCode(65 + index)}
                  </p>
                  <div className="w-1/2">
                    <FormField
                      control={form.control}
                      name={`ingredients.${index}.name`}
                      render={({ field }) => (
                        <FormItem className="flex flex-col items-start justify-start">
                          <FormLabel>Name</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Choose the ingredient name"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="w-1/2">
                    <FormField
                      control={form.control}
                      name={`ingredients.${index}.color`}
                      render={({ field }) => (
                        <FormItem className="flex flex-col items-start">
                          <FormLabel>Color</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Choose the ingredient color"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        onClick={() => remove(index)}
                        variant="destructive"
                        size="icon"
                        className="mt-6"
                      >
                        <TrashIcon className="p-1" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent
                      sideOffset={20}
                      align="end"
                      alignOffset={50}
                      side="left"
                    >
                      Remove ingredient {String.fromCharCode(65 + index)}
                    </TooltipContent>
                  </Tooltip>
                </div>
              ))}
            </div>
            <Button
              className="ml-auto py-2 px-3 text-xs"
              onClick={() => append({ name: "", color: "" })}
            >
              <PlusCircle className="p-1 pl-0"></PlusCircle>Add Ingredient
            </Button>
            <div>
              <p className="font-semibold">Parameters</p>
            </div>
          </form>
          <DialogFooter className="sm:justify-between">
            <DialogClose asChild>
              <Button className="w-1/6" variant="outline">
                Cancel
              </Button>
            </DialogClose>
            <DialogClose disabled={!form.formState.isValid} asChild>
              <Button
                type="submit"
                form="new-simulation-form"
                className="w-1/6"
              >
                Save
              </Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Form>
  );
};
