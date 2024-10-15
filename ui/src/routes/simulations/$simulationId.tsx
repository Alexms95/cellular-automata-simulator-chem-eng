import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { ReactP5Wrapper, Sketch } from "@p5-wrapper/react";
import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useRef, useState } from "react";

export const Route = createFileRoute("/simulations/$simulationId")({
  component: () => <SimulationDetail />,
});

function SimulationDetail() {
  const { simulationId } = Route.useParams();
  const chunks = useRef<Blob[]>([]);

  const [isRecording, setIsRecording] = useState(true);

  const generateVideo = () => {
    const blob = new Blob(chunks.current, { type: "video/mp4" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    document.body.appendChild(a);
    a.href = url;
    a.download = "cellular_automata.mp4";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const memoizedReactP5Wrapper = useMemo(() => {
    const sketch: Sketch = (p5) => {
      let grid: number[][];
      const cols = 100;
      const rows = cols;
      const resolution = 10;
      const frameRate = 5;
      let recorder: MediaRecorder;

      p5.setup = () => {
        p5.createCanvas(500, 500);
        p5.frameRate(frameRate);
        grid = createGrid();
      };

      p5.draw = () => {
        if (p5.frameCount === 1) {
          recorder = new MediaRecorder(
            p5.drawingContext.canvas.captureStream(frameRate)
          );

          recorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
              chunks.current.push(e.data);
            }
          };

          recorder.onstop = () => {
            setIsRecording(false);
          };

          recorder.start();
          return;
        }

        if (p5.frameCount >= 32) {
          if (isRecording) recorder.stop();
          p5.noLoop();
          return;
        }

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
          Array.from({ length: cols }).map(() => p5.random([0, 1]))
        );
      }
    };
    return <ReactP5Wrapper sketch={sketch} />;
  }, []);

  return (
    <div className="flex items-center justify-center gap-2">
      {memoizedReactP5Wrapper}
      <div className="w-1/3 space-y-4">
        <p>Simulation ID: {simulationId}</p>
        <Button
          className="w-1/2"
          disabled={isRecording}
          onClick={generateVideo}
        >
          {isRecording ? (
            <Spinner size="small">
              <span className="ml-2">Running simulation...</span>
            </Spinner>
          ) : (
            "Generate mp4 video"
          )}
        </Button>
      </div>
    </div>
  );
}
