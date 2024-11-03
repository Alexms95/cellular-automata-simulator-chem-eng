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
import httpClient from "@/lib/httpClient";
import { colors } from "@/models/colors";
import { zodResolver } from "@hookform/resolvers/zod";
import { PlusCircle, TrashIcon } from "lucide-react";
import { useEffect } from "react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Separator } from "./ui/separator";
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
      color: z.string(),
      initialNumber: z.coerce
        .number({ message: "It must be a number." })
        .int("It must be an integer number.")
        .positive("It must be a positive number."),
    })
  ),
  parameters: z.object({
    Pm: z.array(
      z.coerce
        .number()
        .gte(0, { message: "It must be greater or equal to 0." })
        .lte(1, { message: "It must be less or equal to 1." })
    ),
    J: z.array(
      z.object({
        from: z.string({ message: "It must be a string." }),
        to: z.string({ message: "It must be a string." }),
        value: z.coerce
          .number()
          .gte(0, { message: "It must be greater or equal to 0." })
          .lte(1, { message: "It must be less or equal to 1." }),
      })
    ),
  }),
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
      ingredients: [{ name: "A", initialNumber: 1, color: "blue" }],
      parameters: {
        Pm: [1],
        J: [{ from: "A", to: "A", value: 1 }],
      },
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "ingredients",
  });

  const generatePairMatrix = (arraySize: number) => {
    const result: number[][] = [];

    for (let i = 0; i < arraySize; i++) {
      for (let j = 0; j < arraySize; j++) {
        result.push([i, j]);
      }
    }

    return result;
  };

  const pairMatrix = generatePairMatrix(fields.length);

  useEffect(() => {
    console.log(form.getValues());
  });

  const onSubmit = (values: NewSimulationForm) => {
    console.log(values);
    httpClient.post("/simulations", values);
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
            <Separator />
            <div className="space-y-2">
              {fields.map((field, index) => (
                <div key={field.id} className="flex space-x-2">
                  <p className="w-1/8 text-sm font-semibold mt-10">
                    Ingredient {String.fromCharCode(65 + index)}
                  </p>
                  <div className="w-1/2">
                    <FormField
                      control={form.control}
                      name={`ingredients.${index}.name`}
                      render={({ field }) => (
                        <FormItem className="">
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
                  <div className="w-1/4">
                    <FormField
                      control={form.control}
                      name={`ingredients.${index}.initialNumber`}
                      defaultValue={1}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Initial number</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="Initial count of the ingredient"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="w-1/5">
                    <FormField
                      control={form.control}
                      name={`ingredients.${index}.color`}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Color</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {colors.map((color) => (
                                <SelectItem key={color.name} value={color.name}>
                                  <div className="flex items-center justify-center">
                                    <span
                                      className="w-4 h-4 rounded-full mr-2"
                                      style={{
                                        backgroundColor: color.hex,
                                      }}
                                    ></span>
                                    {color.name}
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
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
                        className="mt-8"
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
            <FormMessage>
              {form.formState.errors?.ingredients?.root?.message}
            </FormMessage>
            <Button
              className="ml-auto py-2 px-3 text-xs"
              type="button"
              onClick={() =>
                append({
                  name: String.fromCharCode(65 + fields.length),
                  color: colors.filter(
                    (c) =>
                      !form
                        .getValues("ingredients")
                        .flatMap((i) => i.color)
                        .includes(c.name)
                  )[0].name,
                  initialNumber: 1,
                })
              }
            >
              <PlusCircle className="p-1 pl-0"></PlusCircle>Add Ingredient
            </Button>
            <Separator />
            <h4 className="scroll-m-20 font-semibold tracking-tight">
              Parameters
            </h4>
            <div className="flex space-x-2">
              {fields.map((field, index) => (
                <FormField
                  key={field.id}
                  control={form.control}
                  name={`parameters.Pm.${index}`}
                  defaultValue={1}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        P<sub>M</sub> ({String.fromCharCode(65 + index)})
                      </FormLabel>
                      <FormControl>
                        <Input
                          step={0.1}
                          min={0}
                          max={1}
                          type="number"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              ))}
            </div>
            <div className="flex space-x-2">
              {pairMatrix.map((comb, index) => (
                <div key={index}>
                  <FormField
                    control={form.control}
                    name={`parameters.J.${index}.from`}
                    defaultValue={String.fromCharCode(65 + comb[0])}
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Input className="hidden" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name={`parameters.J.${index}.to`}
                    defaultValue={String.fromCharCode(65 + comb[1])}
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Input className="hidden" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name={`parameters.J.${index}.value`}
                    defaultValue={1}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          J (
                          {String.fromCharCode(65 + comb[0]) +
                            String.fromCharCode(65 + comb[1])}
                          )
                        </FormLabel>
                        <FormControl>
                          <Input
                            step={0.1}
                            min={0}
                            max={1}
                            type="number"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              ))}
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
