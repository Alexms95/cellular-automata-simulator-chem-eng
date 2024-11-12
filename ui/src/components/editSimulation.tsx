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
import { formSchema, generatePairMatrix, SimulationForm } from "@/lib/utils";
import { colors } from "@/models/colors";
import { Simulation } from "@/models/simulation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PenIcon, PlusCircle, TrashIcon } from "lucide-react";
import { useEffect } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { toast } from "sonner";
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

export const EditSimulation = ({ id }: { id: string }) => {
  const queryClient = useQueryClient();

  const defaultIngredients = [{ name: "A", initialNumber: 1, color: "blue" }];

  const form = useForm<SimulationForm>({
    resolver: zodResolver(formSchema),
    mode: "onTouched",
    defaultValues: {
      name: "",
      iterationsNumber: 1,
      gridSize: 1,
      ingredients: defaultIngredients,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "ingredients",
  });

  const { data } = useQuery<Simulation[]>({
    queryKey: ["simulations"],
  });

  useEffect(() => {
    if (data) {
      const simulation = data.find((s) => s.id === id);
      if (simulation) {
        form.reset(simulation);
      }
    }
  }, [data, id]);

  const handleRemove = (index: number) => {
    remove(index);
    // Remove the parameters that have the ingredient letter
    const parameters = form.getValues("parameters");
    const newParameters = {
      Pm: parameters.Pm.filter((_, i) => i !== index),
      J: parameters.J.filter(
        (param) =>
          param.fromIngr !== String.fromCharCode(65 + index) &&
          param.toIngr !== String.fromCharCode(65 + index)
      ),
      Pb: parameters.Pb.filter(
        (param) =>
          param.fromIngr !== String.fromCharCode(65 + index) &&
          param.toIngr !== String.fromCharCode(65 + index)
      ),
    };

    form.setValue("parameters", newParameters);
  };

  const pairMatrix = generatePairMatrix(fields.length);

  const saveSimulation = useMutation({
    mutationFn: (values: SimulationForm) =>
      httpClient.put(`/simulations/${id}`, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulations"] });
    },
  });

  const onSubmit = async (values: SimulationForm) => {
    const mutation = saveSimulation.mutateAsync(values);
    toast.promise(mutation, {
      loading: "Saving simulation...",
      success: `Simulation ${values.name} saved!`,
      error: "Error editing simulation",
    });
  };

  const downloadJsonFile = () => {
    const values = form.getValues();
    const file = new Blob([JSON.stringify(form.getValues(), null, "\t")], {
      type: "application/json",
    });
    const a = document.createElement("a");
    const url = URL.createObjectURL(file);
    a.href = url;
    a.download = values.name.replace(" ", "_") + "_inputs.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const fillInForm = (files: FileList | null) => {
    if (files && files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const result = e.target?.result;
        if (typeof result === "string") {
          const values = JSON.parse(result) as SimulationForm;
          form.reset(values);
        }
      };
      reader.readAsText(files[0]);
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <PenIcon className="m-2" />
      </DialogTrigger>
      <DialogContent className="sm:max-w-[80%] overflow-y-scroll max-h-[90%]">
        <DialogHeader>
          <DialogTitle>Edit Simulation</DialogTitle>
          <DialogDescription>
            You are editing this simulation. Save it when you are done.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-between">
          <div className="grid w-full max-w-md items-center gap-2">
            <Label htmlFor="file">Import a configuration file</Label>
            <Input
              onChange={(e) => fillInForm(e.target.files)}
              id="file"
              type="file"
              accept=".json"
            />
            <span className="text-xs text-zinc-500">
              On importing it, all fields will be overwritten.
            </span>
          </div>
          <Button
            variant="secondary"
            type="button"
            onClick={() => form.reset({ ingredients: defaultIngredients })}
          >
            Reset to default
          </Button>
        </div>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="space-y-4 flex flex-col"
            id="new-simulation-form"
          >
            <div className="flex space-x-4">
              <div className="w-1/3">
                <FormField
                  control={form.control}
                  name="name"
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
                  name="gridSize"
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
                      {!form.formState.errors.gridSize && (
                        <FormDescription>
                          A grid of {form.getValues("gridSize")} x{" "}
                          {form.getValues("gridSize")} will be created.
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
                        onClick={() => handleRemove(index)}
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
                  shouldUnregister
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
            <div className="flex space-x-2 flex-wrap">
              {pairMatrix.map((comb, index) => {
                return (
                  <div key={index}>
                    <FormField
                      control={form.control}
                      shouldUnregister
                      name={`parameters.Pb.${index}.fromIngr`}
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
                      name={`parameters.Pb.${index}.toIngr`}
                      shouldUnregister
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
                      name={`parameters.Pb.${index}.value`}
                      shouldUnregister
                      defaultValue={1}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>
                            P<sub>B</sub> (
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
                );
              })}
            </div>
            <div className="flex space-x-2 flex-wrap">
              {pairMatrix.map((comb, index) => {
                return (
                  <div key={index}>
                    <FormField
                      control={form.control}
                      shouldUnregister
                      name={`parameters.J.${index}.fromIngr`}
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
                      name={`parameters.J.${index}.toIngr`}
                      shouldUnregister
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
                      shouldUnregister
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
                );
              })}
            </div>
          </form>
        </Form>
        <DialogFooter className="sm:justify-between">
          <DialogClose asChild>
            <Button className="w-1/6" variant="outline">
              Cancel
            </Button>
          </DialogClose>
          <Tooltip>
            <TooltipTrigger asChild>
              <div>
                <Button
                  disabled={!form.formState.isValid}
                  variant="secondary"
                  onClick={downloadJsonFile}
                >
                  Export Config File
                </Button>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              {" "}
              {form.formState.isValid ? (
                <span>Download the simulation configuration file</span>
              ) : (
                <span>
                  Check if all fields are accordingly filled in before
                  downloading the simulation file
                </span>
              )}{" "}
            </TooltipContent>
          </Tooltip>
          <DialogClose disabled={!form.formState.isValid} asChild>
            <Button type="submit" form="new-simulation-form" className="w-1/6">
              Save
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
