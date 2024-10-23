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
import { PlusCircle } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
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
  ingredientsNumber: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
  namesOfIngredients: z.array(
    z.string({ message: "Name required" }).min(1, {
      message: "It must be at least 1 character.",
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
      ingredientsNumber: 1,
      namesOfIngredients: ["A"],
    },
  });

  const ingredientsNumber = form.watch("ingredientsNumber");

  const onSubmit = (values: NewSimulationForm) => {
    console.log(values);
  };

  useEffect(() => {
    const currentLength = form.getValues("namesOfIngredients")?.length || 0;

    if (ingredientsNumber < currentLength) {
      form.setValue(
        "namesOfIngredients",
        form
          .getValues("namesOfIngredients")
          .slice(0, -(currentLength - ingredientsNumber))
      );
      form.trigger("namesOfIngredients");
    }
  }, [ingredientsNumber, form]);

  return (
    <Form {...form}>
      <Dialog>
        <DialogTrigger asChild>
          <Button className="self-end mr-4">
            <PlusCircle className="mr-2"></PlusCircle>New Simulation
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[1000px]">
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
            <div className="flex space-x-4">
              <div className="w-1/2">
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
              <div className="w-1/2">
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
              <div className="w-1/2">
                <FormField
                  control={form.control}
                  name="ingredientsNumber"
                  render={({ field }) => (
                    <FormItem className="flex flex-col items-start">
                      <FormLabel>Number of Ingredients</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Choose the number of ingredients"
                          type="number"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        For default, the ingredients will be named as{" "}
                        <strong>A</strong>, <strong>B</strong>,{" "}
                        <strong>C</strong>, etc.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
            <div className="flex space-x-4">
              {ingredientsNumber > 0 &&
                Array.from({ length: ingredientsNumber }).map((_, index) => (
                  <div key={index} className="w-1/2">
                    <FormField
                      control={form.control}
                      defaultValue={String.fromCharCode(65 + index)}
                      name={`namesOfIngredients.${index}`}
                      shouldUnregister
                      render={({ field }) => (
                        <FormItem className="flex flex-col items-start">
                          <FormLabel>
                            {String.fromCharCode(65 + index)} will be
                          </FormLabel>
                          <FormControl>
                            <Input {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                ))}
            </div>
          </form>
          <DialogFooter>
            <DialogClose disabled={!form.formState.isValid} asChild>
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
    </Form>
  );
};
