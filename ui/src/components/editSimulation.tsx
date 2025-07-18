import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input, InputWithIcon } from "@/components/ui/input";
import httpClient from "@/lib/httpClient";
import {
  calculateFractions,
  formSchema,
  generatePairMatrix,
  SimulationForm,
} from "@/lib/utils";
import { colors } from "@/models/colors";
import { Simulation } from "@/models/simulation";
import { zodResolver } from "@hookform/resolvers/zod";
import { InfoCircledIcon } from "@radix-ui/react-icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRightIcon,
  PenIcon,
  Percent,
  PlusCircle,
  PlusIcon,
  TrashIcon,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useFieldArray, useForm, useWatch } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
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

export const EditSimulation = ({
  id,
  complete = false,
  disabled = false,
}: {
  id: string;
  complete: boolean;
  disabled: boolean;
}) => {
  const queryClient = useQueryClient();

  const defaultIngredients = [{ name: "A", molarFraction: 1, color: "blue" }];

  const form = useForm<SimulationForm>({
    resolver: zodResolver(formSchema),
    mode: "onTouched",
    defaultValues: {
      name: "",
      iterationsNumber: 1,
      gridHeight: 1,
      gridLenght: 1,
      ingredients: defaultIngredients,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "ingredients",
  });

  const reactionsFieldArray = useFieldArray({
    control: form.control,
    name: "reactions",
  });

  const componentIndexNames = useWatch({
    control: form.control,
    name: "ingredients",
  }).map((ingredient, i) => ({
    index: String.fromCharCode(i + 65),
    name: ingredient.name,
  }));

  const { data } = useQuery<Simulation[]>({
    queryKey: ["simulations"],
  });

  const resetSimulationData = useCallback(
    (data?: Simulation[]) => {
      if (data) {
        const simulation = data.find((s) => s.id === id);
        if (simulation) {
          form.reset(simulation);
        }
      }
    },
    [form, id]
  );

  const [componentsCount, setComponentsCount] = useState<number[]>([]);

  const ingredients = useWatch({ control: form.control, name: "ingredients" });
  const totalCells =
    useWatch({ control: form.control, name: "gridLenght" }) *
    useWatch({ control: form.control, name: "gridHeight" });

  const calculateComponentsCount = useCallback(
    (total: number, percentages: number[]) =>
      calculateFractions(total, percentages),
    []
  );

  const reactions = useWatch({ control: form.control, name: "reactions" });

  useEffect(() => {
    // Adjust Pr and reversePr if there is no intermediate
    reactions?.forEach((reaction) => {
      const hasIntermediate = reaction.hasIntermediate;
      if (!hasIntermediate && reaction.Pr.length > 1) {
        reaction.Pr = reaction.Pr.slice(0, 1);
        reaction.reversePr = reaction.reversePr.slice(0, 1);
        form.setValue("reactions", reactions);
      } else if (hasIntermediate && reaction.Pr.length < 2) {
        reaction.Pr.push(0);
        reaction.reversePr.push(0);
        form.setValue("reactions", reactions);
      }
    });
  }, [reactions, form]);

  useEffect(() => {
    if (ingredients && totalCells > 0) {
      const percentages = ingredients.map(
        (i: { molarFraction: number }) => i.molarFraction
      );
      const calculatedComponents = calculateComponentsCount(
        totalCells,
        percentages
      );
      setComponentsCount(calculatedComponents);
    }
  }, [ingredients, totalCells, calculateComponentsCount]);

  const handleRemove = (index: number) => {
    remove(index);
    // Remove the parameters that have the ingredient letter
    const parameters = form.getValues("parameters");
    const newParameters = {
      Pm: parameters.Pm.filter((_, i) => i !== index),
      J: parameters.J.filter(
        (param) => !param.relation.includes(String.fromCharCode(65 + index))
      ),
    };

    const rotationComponent = form.getValues("rotation.component");
    if (rotationComponent === String.fromCharCode(65 + index))
      form.setValue("rotation.component", "None");

    form.setValue("parameters", newParameters);
  };

  const rotationComponent = useWatch({
    control: form.control,
    name: "rotation.component",
  });

  const [pairMatrix, setPairMatrix] = useState<string[][]>([]);

  useEffect(() => {
    setPairMatrix(generatePairMatrix(fields.length, rotationComponent));
    if (rotationComponent === "None") {
      form.setValue("rotation.Prot", 0);
    }
  }, [rotationComponent, fields.length, form]);

  useEffect(() => {
    const parameterJ = pairMatrix.map((pair, index) => ({
      relation: pair.join("|"),
      value: form.getValues(`parameters.J.${index}.value`) || 1,
    }));
    form.setValue("parameters.J", parameterJ, { shouldDirty: true });
  }, [pairMatrix, form]);

  const molarFractionsSum = fields
    .map((_, index) => form.watch(`ingredients.${index}.molarFraction`))
    .reduce((acc, curr) => acc + Number(curr), 0);

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
      error: (error) => {
        const message = error.response?.data?.detail;
        return message ?? `Error editing simulation ${values.name}`;
      },
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
          form.reset({ ...values, name: values.name + "_new" });
        }
      };
      reader.readAsText(files[0]);
    }
  };

  return (
    <Dialog>
      <DialogTrigger onClick={() => resetSimulationData(data)} asChild>
        {complete ? (
          <Button
            variant="outline"
            className="flex items-center justify-center gap-2 dark:text-zinc-900 dark:bg-white"
            disabled={disabled}
          >
            <PenIcon className="h-4 w-4" />
            Edit Simulation
          </Button>
        ) : (
          <Button
            variant="outline"
            size="icon"
            className="w-8 h-8"
            disabled={disabled}
          >
            <PenIcon className="m-2" />
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[80%] overflow-y-scroll max-h-[90%] dark:text-white">
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
              <div className="w-1/2">
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
              <div>
                <div className="flex gap-4">
                  <div className="w-1/2">
                    <FormField
                      control={form.control}
                      name="gridHeight"
                      render={({ field }) => (
                        <FormItem className="flex flex-col items-start">
                          <FormLabel>Number of Lines</FormLabel>
                          <FormControl>
                            <Input min={1} type="number" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="w-1/2">
                    <FormField
                      control={form.control}
                      name="gridLenght"
                      render={({ field }) => (
                        <FormItem className="flex flex-col items-start">
                          <FormLabel>Number of Columns</FormLabel>
                          <FormControl>
                            <Input min={1} type="number" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
                {!form.formState.errors.gridHeight &&
                  !form.formState.errors.gridLenght && (
                    <FormDescription className="mt-2">
                      A grid of {form.watch("gridHeight")} x{" "}
                      {form.watch("gridLenght")} will be created (
                      {form.watch("gridLenght") * form.watch("gridHeight")}{" "}
                      cells).
                    </FormDescription>
                  )}
              </div>
            </div>
            <Separator />
            <div className="space-y-2">
              {fields.map((field, index) => (
                <div key={field.id} className="flex space-x-2">
                  <p className="w-1/8 text-sm font-semibold mt-10">
                    Component {String.fromCharCode(65 + index)}
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
                              placeholder="Choose the component name"
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
                  <div className="w-1/5">
                    <FormField
                      control={form.control}
                      name={`ingredients.${index}.molarFraction`}
                      defaultValue={0}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Molar Fraction</FormLabel>
                          <FormControl>
                            <InputWithIcon
                              step={0.1}
                              type="number"
                              endIcon={Percent}
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Approx. {componentsCount[index]} cells
                          </FormDescription>
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
                      Remove component {String.fromCharCode(65 + index)}
                    </TooltipContent>
                  </Tooltip>
                </div>
              ))}
            </div>
            {molarFractionsSum !== 100 && (
              <FormMessage>
                The sum of molar fractions must be 100%. Current:{" "}
                {`${molarFractionsSum}%`}.
              </FormMessage>
            )}
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
                  molarFraction: 0,
                })
              }
            >
              <PlusCircle className="p-1 pl-0"></PlusCircle>Add Component
            </Button>
            <Separator />
            <h4 className="scroll-m-20 font-semibold tracking-tight">
              Reaction Parameters
            </h4>
            <div className="flex flex-col space-y-8">
              <div className="flex flex-col space-y-2">
                {reactionsFieldArray.fields.map((reacField, index) => (
                  <div key={reacField.id} className="flex flex-col space-y-2">
                    <div className="flex w-full gap-2">
                      <div className="w-1/6">
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.reactants.0`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Reactant 1</FormLabel>
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
                                  {componentIndexNames.map((c) => (
                                    <SelectItem key={c.name} value={c.index}>
                                      {c.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <PlusIcon className="self-end pb-2"></PlusIcon>
                      <div className="w-1/6">
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.reactants.1`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Reactant 2</FormLabel>
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
                                  {componentIndexNames.map((c) => (
                                    <SelectItem key={c.name} value={c.index}>
                                      {c.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <ArrowRightIcon
                        color="green"
                        className="self-end pb-2"
                      ></ArrowRightIcon>
                      <div className="w-1/6">
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.products.0`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Product 1</FormLabel>
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
                                  {componentIndexNames.map((c) => (
                                    <SelectItem key={c.name} value={c.index}>
                                      {c.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <PlusIcon className="self-end pb-2"></PlusIcon>
                      <div className="w-1/6">
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.products.1`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Product 2</FormLabel>
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
                                  {componentIndexNames.map((c) => (
                                    <SelectItem key={c.name} value={c.index}>
                                      {c.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <div className="w-1/6 p-2">
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.hasIntermediate`}
                          render={({ field }) => (
                            <FormItem className="flex flex-col items-center">
                              <FormLabel className="mb-2">
                                Has intermediate?
                              </FormLabel>
                              <FormControl className="p-auto">
                                <Checkbox
                                  checked={field.value}
                                  onCheckedChange={field.onChange}
                                />
                              </FormControl>
                            </FormItem>
                          )}
                        />
                      </div>
                      <Tooltip>
                        <TooltipTrigger className="ml-auto self-end" asChild>
                          <Button
                            onClick={() => reactionsFieldArray.remove(index)}
                            variant="destructive"
                            size="icon"
                            className="mt-8"
                          >
                            <TrashIcon className="p-1" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent
                          sideOffset={10}
                          align="end"
                          alignOffset={50}
                          side="left"
                        >
                          Remove reaction
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <div className="flex space-x-4">
                      <FormField
                        control={form.control}
                        name={`reactions.${index}.Pr.0`}
                        defaultValue={0}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>
                              P<sub>r</sub> (Reactants -&gt;{" "}
                              {form.watch(`reactions.${index}.hasIntermediate`)
                                ? "Intermediate"
                                : "Products"}
                              )
                            </FormLabel>
                            <FormControl>
                              <Input
                                step={0.0001}
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
                      {form.watch(`reactions.${index}.hasIntermediate`) && (
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.Pr.1`}
                          defaultValue={0}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>
                                P<sub>r</sub> (Intermediate -&gt; Products)
                              </FormLabel>
                              <FormControl>
                                <Input
                                  step={0.0001}
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
                      )}
                      <FormField
                        control={form.control}
                        name={`reactions.${index}.reversePr.0`}
                        defaultValue={0}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>
                              Reverse P<sub>r</sub> (
                              {form.watch(`reactions.${index}.hasIntermediate`)
                                ? "Intermediate"
                                : "Products"}{" "}
                              -&gt; Reactants)
                            </FormLabel>
                            <FormControl>
                              <Input
                                step={0.0001}
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
                      {form.watch(`reactions.${index}.hasIntermediate`) && (
                        <FormField
                          control={form.control}
                          name={`reactions.${index}.reversePr.1`}
                          defaultValue={0}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>
                                Reverse P<sub>r</sub> (Products -&gt;
                                Intermediate)
                              </FormLabel>
                              <FormControl>
                                <Input
                                  step={0.0001}
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
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <Button
                className="ml-auto py-2 px-3 text-xs"
                type="button"
                onClick={() =>
                  reactionsFieldArray.append({
                    reactants: [],
                    products: [],
                    hasIntermediate: false,
                    Pr: [],
                    reversePr: [],
                  })
                }
              >
                <PlusCircle className="p-1 pl-0"></PlusCircle>Add Reaction
              </Button>
            </div>
            <Separator />
            <h4 className="scroll-m-20 font-semibold tracking-tight">
              Rotation Parameters
            </h4>
            <div className="flex space-x-4">
              <div className="w-1/4">
                <FormField
                  control={form.control}
                  name="rotation.component"
                  defaultValue="None"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Component</FormLabel>
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
                          <SelectItem key="None" value="None">
                            None
                          </SelectItem>
                          {componentIndexNames.map((c) => (
                            <SelectItem key={c.name} value={c.index}>
                              {c.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <div className="w-1/10">
                <FormField
                  control={form.control}
                  name="rotation.Prot"
                  defaultValue={0}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        P<sub>rot</sub>
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
            </div>
            <Separator />
            <div className="flex items-center gap-4">
              <h4 className="scroll-m-20 font-semibold tracking-tight">
                Movement Parameters
              </h4>
              <Tooltip>
                <TooltipTrigger asChild>
                  <InfoCircledIcon>
                  </InfoCircledIcon>
                </TooltipTrigger>
                <TooltipContent>
                  {componentIndexNames.map((c) => (
                    <div key={c.index}>
                      {c.index}: ({c.name})
                    </div>
                  ))}
                </TooltipContent>
              </Tooltip>
            </div>
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
                          step={0.01}
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
                  <div key={comb.join("|") + index} className="w-1/10">
                    <input
                      key={index}
                      type="hidden"
                      {...form.register(`parameters.J.${index}.relation`)}
                    />
                    <FormField
                      control={form.control}
                      name={`parameters.J.${index}.value`}
                      defaultValue={0}
                      shouldUnregister
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>J ({comb.join("|")})</FormLabel>
                          <FormControl>
                            <Input
                              step={0.01}
                              min={0}
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
