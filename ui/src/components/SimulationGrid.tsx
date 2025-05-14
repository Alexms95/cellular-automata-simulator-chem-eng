import { getDirectionalStyle } from "@/lib/utils";
import { Simulation } from "@/models/simulation";
import clsx from "clsx";
import { FixedSizeList } from "react-window";

interface Props {
  iterations: number[][][];
  ingredients: Simulation["ingredients"];
  rotationComponent?: string;
  reactions?: Simulation["reactions"];
}

const IterationRow = ({ data, index, style }) => {
  const { iterations, ingredients } = data;
  const iteration = iterations[index];
  const gridSize = iteration[0].length;

  return (
    <div style={style} className="flex flex-col gap-2 items-center py-2">
      <h2 className="text-lg font-bold">Iteration {index}</h2>
      <FixedSizeList
        height={550}
        width={gridSize * 16}
        itemCount={iteration.length}
        itemSize={16}
        itemData={{ row: iteration, ingredients }}
        className="overflow-x-hidden"
      >
        {GridRow}
      </FixedSizeList>
    </div>
  );
};

const GridRow = ({ data, index, style }) => {
  const { row, ingredients } = data;

  return (
    <div style={style} className="flex gap-1">
      {row[index].map((cell: number, cellIndex: number) => (
        <div
          key={cellIndex}
          className={clsx(
            "w-3 h-3",
            cell === 0 && "bg-gray-200",
            cell > 200 && "bg-yellow-500",
            cell > 10 && cell < 200 && getDirectionalStyle(cell),
            cell <= 10 && `bg-${ingredients[cell - 1]?.color}-500`
          )}
        />
      ))}
    </div>
  );
};

export default function SimulationGrid({
  iterations,
  ingredients
}: Props) {
  return (
    <div className="space-y-4">
      <FixedSizeList
        height={600}
        width="100%"
        itemCount={iterations.length}
        itemSize={550}
        itemData={{ iterations, ingredients }}
      >
        {IterationRow}
      </FixedSizeList>
    </div>
  );
}
