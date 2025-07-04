import { Simulation } from "@/models/simulation";
import { forwardRef, useEffect, useRef, useState } from "react";
import { FixedSizeList } from "react-window";

interface Props {
  iterations: number[][][];
  ingredients: Simulation["ingredients"];
  currentPage: number;
  rotationComponent?: string;
  reactions?: Simulation["reactions"];
}

const CELL_SIZE = 16; // px

function getCellColor(
  cell: number,
  ingredients: Simulation["ingredients"]
): string {
  if (cell === 0) return "#e5e7eb"; // bg-gray-200
  if (cell > 200) return "#f59e42"; // bg-yellow-500
  if (cell > 10 && cell < 200) {
    return "#bae6fd"; // light blue
  }
  if (cell <= 10) {
    const color = ingredients[cell - 1]?.color || "gray";
    const colorMap: Record<string, string> = {
      red: "#ef4444",
      blue: "#3b82f6",
      green: "#22c55e",
      yellow: "#eab308",
      purple: "#a21caf",
      pink: "#ec4899",
      gray: "#6b7280",
      orange: "#f97316",
    };
    return colorMap[color] || "#6b7280";
  }
  return "#6b7280";
}

const IterationRow = ({
  data,
  index,
  style,
}: {
  data: {
    iterations: number[][][];
    ingredients: Simulation["ingredients"];
    currentPage: number;
  };
  index: number;
  style: React.CSSProperties;
}) => {
  const { iterations, ingredients, currentPage } = data;
  const iteration = iterations[index];
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (!iteration || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let row = 0; row < iteration.length; row++) {
      for (let col = 0; col < iteration[row].length; col++) {
        const cell = iteration[row][col];
        ctx.fillStyle = getCellColor(cell, ingredients);
        ctx.fillRect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        // Draw direction indicator for directional cells
        if (cell > 10 && cell < 200) {
          ctx.save();
          ctx.translate(
            col * CELL_SIZE + CELL_SIZE / 2,
            row * CELL_SIZE + CELL_SIZE / 2
          );
          let deg = 0;
          if (cell % 10 === 2) deg = 270; // left
          else if (cell % 10 === 3) deg = 180; // down
          else if (cell % 10 === 4) deg = 90; // right
          ctx.rotate((deg * Math.PI) / 180);
          ctx.beginPath();
          ctx.moveTo(0, -CELL_SIZE / 2);
          ctx.lineTo(CELL_SIZE / 2, CELL_SIZE / 16);
          ctx.lineTo(-CELL_SIZE / 2, CELL_SIZE / 16);
          ctx.closePath();
          ctx.fillStyle = "#92400e";
          ctx.fill();
          ctx.restore();
        }
      }
    }
  }, [iteration, ingredients]);

  const rows = iteration?.length || 0;
  const cols = iteration?.[0]?.length || 0;

  return (
    <div style={style} className="flex flex-col gap-2 items-center py-2">
      <h2 className="text-lg font-bold text-gray-800 dark:text-gray-200">
        Iteration {index + (currentPage - 1) * 1000}
      </h2>
      <canvas
        ref={canvasRef}
        width={cols * CELL_SIZE}
        height={rows * CELL_SIZE}
        style={{ border: "1px solid #e5e7eb" }}
      />
    </div>
  );
};

const SimulationGrid = forwardRef<
  FixedSizeList<{
    iterations: number[][][];
    ingredients: Simulation["ingredients"];
    currentPage: number;
  }> | null,
  Props
>(function SimulationGrid(
  { iterations, ingredients, currentPage }: Props,
  ref
) {
  const [height, setHeight] = useState(window.innerHeight * 0.8);

  useEffect(() => {
    const handleResize = () => setHeight(window.innerHeight * 0.8);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className="">
      <FixedSizeList
        height={height}
        width="85%"
        itemCount={iterations.length}
        itemSize={20 * (iterations[0].length + 1)}
        itemData={{ iterations, ingredients, currentPage }}
        ref={ref}
      >
        {IterationRow}
      </FixedSizeList>
    </div>
  );
});

export default SimulationGrid;
