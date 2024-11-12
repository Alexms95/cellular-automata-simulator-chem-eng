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
  gridSize: z.coerce
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
        .number({ message: "It must be a number." })
        .positive("It must be a positive number.")
        .gte(0, "It must be greater or equal to 0.")
        .lte(1, "It must be less or equal to 1.")
    ),
    J: z.array(
      z.object({
        fromIngr: z.string({ message: "It must be a string." }),
        toIngr: z.string({ message: "It must be a string." }),
        value: z.coerce
          .number({ message: "It must be a number." })
          .positive("It must be a positive number.")
          .gte(0, "It must be greater or equal to 0.")
          .lte(1, "It must be less or equal to 1."),
      })
    ),
    Pb: z.array(
      z.object({
        fromIngr: z.string({ message: "It must be a string." }),
        toIngr: z.string({ message: "It must be a string." }),
        value: z.coerce
          .number({ message: "It must be a number." })
          .positive("It must be a positive number.")
          .gte(0, "It must be greater or equal to 0.")
          .lte(1, "It must be less or equal to 1."),
      })
    ),
  }),
});

export function generatePairMatrix(arraySize: number) {
  const lastIndex = arraySize - 1;

  // Arrays separados para pares com e sem o último índice
  const pairsWithLast: number[][] = [];
  const pairsWithoutLast: number[][] = [];

  // Gera todas as combinações possíveis de pares
  for (let i = 0; i < arraySize; i++) {
    for (let j = 0; j < arraySize; j++) {
      // Se algum elemento do par for igual a (arraySize - 1),
      // adiciona ao array de pares com último índice
      if (i === lastIndex || j === lastIndex) {
        pairsWithLast.push([i, j]);
      } else {
        pairsWithoutLast.push([i, j]);
      }
    }
  }

  // Concatena os arrays, colocando os pares com último índice no final
  return [...pairsWithoutLast, ...pairsWithLast];
}