import { ReactP5Wrapper, Sketch } from "@p5-wrapper/react";
import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/about")({
  component: About,
});

function About() {
  const sketch: Sketch = (p5) => {
    let grid: number[][];
    const cols = 10;
    const rows = cols;
    const resolution = 50;

    p5.setup = () => {
      p5.createCanvas(500, 500);
      p5.frameRate(5);
      grid = createGrid();
    };

    p5.draw = () => {
      p5.background(220);
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = i * resolution;
          const y = j * resolution;
          if (grid[j][i] === 1) {
            p5.fill("orange");
            p5.stroke(220);
            p5.rect(x, y, resolution - 1, resolution - 1);
          } else {
            p5.fill("blue");
            p5.stroke(220);
            p5.rect(x, y, resolution - 1, resolution - 1);
          }
        }
      }
      grid = createGrid();
    };

    function createGrid() {
      return Array.from({ length: rows }).map(() =>
        Array.from({ length: cols }).map(() => Math.floor(p5.random([0, 1])))
      );
    }
  };

  return (
    <div className="flex justify-center">
      <ReactP5Wrapper sketch={sketch} />
    </div>
  );
}
