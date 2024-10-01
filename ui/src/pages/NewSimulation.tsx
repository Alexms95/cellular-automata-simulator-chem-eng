import { Button } from "@/components/ui/button";
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
import { useForm } from "react-hook-form";
import { z } from "zod";

const formSchema = z.object({
  simulationName: z.string().min(3, {
    message: "It must be at least 3 characters.",
  }),
  iterationsNumber: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
});

export const NewSimulation = () => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      simulationName: "",
      iterationsNumber: 1,
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    console.log(values);
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-4 w-1/5 flex flex-col"
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
              <FormDescription>Choose an easy-to-find name.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="iterationsNumber"
          render={({ field }) => (
            <FormItem className="flex flex-col items-start">
              <FormLabel>Iterations Number</FormLabel>
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
        <Button type="submit">Run Simulation</Button>
      </form>
    </Form>
  );
};
