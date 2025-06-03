import { getDirectionalStyle } from "@/lib/utils";
import { Simulation } from "@/models/simulation";
import clsx from "clsx";
import { forwardRef, useEffect, useState } from "react";
import { FixedSizeList } from "react-window";

interface Props {
  iterations: number[][][];
  ingredients: Simulation["ingredients"];
  rotationComponent?: string;
  reactions?: Simulation["reactions"];
}

const IterationRow = ({
  data,
  index,
  style,
}: {
  data: { iterations: number[][][]; ingredients: Simulation["ingredients"] };
  index: number;
  style: React.CSSProperties;
}) => {
  const { iterations, ingredients } = data;
  const iteration = iterations[index];

  return (
    <div style={style} className="flex flex-col gap-2 items-center py-2">
      <h2 className="text-lg font-bold">Iteration {index}</h2>
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${iteration[0].length}, 1fr)` }}
      >
        {iteration.map((row, rowIndex) =>
          row.map((cell: number, cellIndex: number) => (
            <div
              key={`${rowIndex}-${cellIndex}`}
              className={clsx(
                "w-3 h-3",
                cell === 0 && "bg-gray-200",
                cell > 200 && "bg-yellow-500",
                cell > 10 && cell < 200 && getDirectionalStyle(cell),
                cell <= 10 && `bg-${ingredients[cell - 1]?.color}-500`
              )}
            />
          ))
        )}
      </div>
    </div>
  );
};

const SimulationGrid = forwardRef<
  FixedSizeList<{
    iterations: number[][][];
    ingredients: Simulation["ingredients"];
  }> | null,
  Props
>(function SimulationGrid({ iterations, ingredients }: Props, ref) {
  const [height, setHeight] = useState(window.innerHeight * 0.80);

  useEffect(() => {
    const handleResize = () => setHeight(window.innerHeight * 0.80);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className="">
      <FixedSizeList
        height={height}
        width="70%"
        itemCount={iterations.length}
        itemSize={20 * (iterations[0].length + 1)}
        itemData={{ iterations, ingredients }}
        ref={ref}
      >
        {IterationRow}
      </FixedSizeList>
    </div>
  );
});

export default SimulationGrid;
