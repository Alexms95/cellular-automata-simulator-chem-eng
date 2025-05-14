// components/SimulationGrid.tsx
import clsx from "clsx";
import { getDirectionalStyle } from "@/lib/utils";
import { Simulation } from "@/models/simulation";

interface Props {
  iterations: number[][][];
  ingredients: Simulation["ingredients"];
  rotationComponent?: string;
  reactions?: Simulation["reactions"];
}

export default function SimulationGrid({
  iterations,
  ingredients,
  rotationComponent,
  reactions,
}: Props) {
  return (
    <div className="space-y-4">
      {iterations.map((iteration, index) => (
        <div key={index} className="flex flex-col gap-2 items-center">
          <h2 className="text-lg font-bold">Iteration {index}</h2>
          <div className={`grid grid-cols-${iteration[0].length} gap-2`}>
            {iteration.map((row, rowIndex) => (
              <div key={rowIndex} className="flex gap-2">
                {row.map((cell, cellIndex) => (
                  <div
                    key={cellIndex}
                    className={clsx(
                      "w-4 h-4",
                      cell === 0 && "bg-gray-200",
                      cell > 200 && "bg-yellow-500",
                      cell > 10 && cell < 200 && getDirectionalStyle(cell),
                      cell <= 10 && `bg-${ingredients[cell - 1]?.color}-500`
                    )}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
