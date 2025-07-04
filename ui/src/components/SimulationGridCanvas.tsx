import { Simulation } from "@/models/simulation";
import { useEffect, useRef } from "react";

interface Props {
  iterations: number[][][];
  ingredients: Simulation["ingredients"];
  currentPage: number;
  rotationComponent?: string;
  reactions?: Simulation["reactions"];
}

const CELL_SIZE = 8; // px

function getCellColor(
  cell: number,
  ingredients: Simulation["ingredients"]
): string {
  if (cell === 0) return "#e5e7eb"; // bg-gray-200
  if (cell > 200) return "#f59e42"; // bg-yellow-500
  if (cell > 10 && cell < 200) {
    // Use a light background for directional cells
    return "#bae6fd"; // light blue
  }
  if (cell <= 10) {
    const color = ingredients[cell - 1]?.color || "gray";
    // Map tailwind color names to hex, fallback to gray
    const colorMap: Record<string, string> = {
      red: "#ef4444",
      blue: "#3b82f6",
      green: "#22c55e",
      yellow: "#eab308",
      purple: "#a21caf",
      pink: "#ec4899",
      gray: "#6b7280",
      orange: "#f97316",
      // add more as needed
    };
    return colorMap[color] || "#6b7280";
  }
  return "#6b7280";
}

// Helper to extract rotation from class string (e.g., "rotate-90")
function getRotationDegrees(style: string): number {
  if (!style) return 0;
  const match = style.match(/rotate-(\d+)/);
  if (match) {
    return parseInt(match[1], 10);
  }
  if (style.includes("rotate-180")) return 180;
  if (style.includes("rotate-90")) return 90;
  if (style.includes("rotate-270")) return 270;
  return 0;
}

const SimulationGridCanvas = ({
  iterations,
  ingredients,
  currentPage,
}: Props) => {
  // One ref per iteration
  const canvasRefs = useRef<(HTMLCanvasElement | null)[]>([]);

  useEffect(() => {
    iterations.forEach((iteration, idx) => {
      const canvas = canvasRefs.current[idx];
      if (!iteration || !canvas) return;
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
            //const style = getDirectionalStyle(cell);
            // Default arrow color
            ctx.save();
            ctx.translate(
              col * CELL_SIZE + CELL_SIZE / 2,
              row * CELL_SIZE + CELL_SIZE / 2
            );
            // Determine rotation
            let deg = 0;
            if (cell % 4 === 2) deg = 90;
            else if (cell % 4 === 3) deg = 180;
            else if (cell % 4 === 4) deg = 270;
            // else deg = 0 (default)
            ctx.rotate((deg * Math.PI) / 180);

            // Draw a triangle pointing "up" (will be rotated)
            ctx.beginPath();
            ctx.moveTo(0, -CELL_SIZE / 2); // tip
            ctx.lineTo(CELL_SIZE / 2, CELL_SIZE / 8); // bottom right
            ctx.lineTo(-CELL_SIZE / 2, CELL_SIZE / 8); // bottom left
            ctx.closePath();
            ctx.fillStyle = "#92400e"; // brown-600 for arrow
            ctx.fill();
            ctx.restore();
          }
        }
      }
    });
  }, [iterations, ingredients, currentPage]);

  return (
    <div className="flex flex-col items-center gap-8">
      {iterations.map((iteration, idx) => {
        const rows = iteration?.length || 0;
        const cols = iteration?.[0]?.length || 0;
        return (
          <div key={idx} className="flex flex-col items-center">
            <h2 className="text-lg font-bold mb-2">
              Iteration {idx + currentPage * 1000}
            </h2>
            <canvas
              ref={(el) => (canvasRefs.current[idx] = el)}
              width={cols * CELL_SIZE}
              height={rows * CELL_SIZE}
              style={{ border: "1px solid #e5e7eb" }}
            />
          </div>
        );
      })}
    </div>
  );
};

export default SimulationGridCanvas;
