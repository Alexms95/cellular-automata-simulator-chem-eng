import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { z } from "zod";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type SimulationForm = z.infer<typeof formSchema>;

export const formSchema = z.object({
  name: z.string().min(3, {
    message: "It must be at least 3 characters.",
  }),
  iterationsNumber: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
  gridHeight: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
  gridLenght: z.coerce
    .number({ message: "It must be a number." })
    .int("It must be an integer number.")
    .positive("It must be a positive number."),
  ingredients: z
    .array(
      z.object({
        name: z.string().min(1, {
          message: "It must be at least 1 character.",
        }),
        color: z.string(),
        molarFraction: z.coerce
          .number({ message: "It must be a number." })
          .gte(0, "It must be greater or equal to 0.")
          .lte(100, "It must be less or equal to 100."),
      }),
    )
    .superRefine((value, ctx) => {
      const sum = value.reduce(
        (acc, curr) => acc + Number(curr.molarFraction),
        0,
      );

      if (sum !== 100) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `The sum of molar fractions must be 100.`,
        });
      }
    }),
  parameters: z.object({
    Pm: z.array(
      z.coerce
        .number({ message: "It must be a number." })
        .gte(0, "It must be greater or equal to 0.")
        .lte(1, "It must be less or equal to 1."),
    ),
    J: z.array(
      z.object({
        fromIngr: z.string(),
        toIngr: z.string(),
        value: z.coerce
          .number({ message: "It must be a number." })
          .gte(0, "It must be greater or equal to 0.")
      }),
    ),
  }),
});

export function generatePairMatrix(arraySize: number) {
  const result: number[][] = [];

  for (let i = 0; i < arraySize; i++) {
    for (let j = 0; j <= i; j++) {
      result.push([j, i]);
    }
  }

  return result;
}

export function calculateFractions(
  total: number,
  percentages: number[],
): number[] {
  const accSum = (acc: number, curr: number) => acc + curr;

  const fractions = percentages.map((p) => (p ? (p / 100) * total : 0));

  const roundedFractions = fractions.map(Math.floor);
  const error = Math.abs(
    fractions.reduce(accSum, 0) - roundedFractions.reduce(accSum, 0),
  );

  if (error === 0) return roundedFractions;

  const adjustments = [
    ...fractions.map((value, index) => ({
      index,
      difference: value - roundedFractions[index],
    })),
  ];

  adjustments.sort((a, b) => b.difference - a.difference);

  for (let i = 0; i < error; i++) {
    roundedFractions[adjustments[i].index]++;
  }

  return roundedFractions;
}
