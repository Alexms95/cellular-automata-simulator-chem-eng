import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import httpClient from "@/lib/httpClient";
import { Simulation } from "@/models/simulation";
import { ReactP5Wrapper, Sketch } from "@p5-wrapper/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import clsx from "clsx";
import pako from "pako";
import { useMemo, useRef, useState } from "react";
import { toast } from "sonner";

export const Route = createFileRoute("/simulations/$simulationId")({
  component: () => <SimulationDetail />,
});

function SimulationDetail() {
  const { simulationId } = Route.useParams();

  const queryClient = useQueryClient();

  const { data, isLoading, isFetching } = useQuery<Simulation>({
    queryKey: ["simulations", simulationId],
  });


  const compressedIterations = data?.iterations

  //compressedIterations is a string of bytes zipped with gzip, it must be firstly base64 decoded, then decompressed with pako
  const decompressedIterations = useMemo(() => {
    if (!compressedIterations) return null;
    const binaryString = atob(compressedIterations);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const decompressed = pako.inflate(bytes, { to: "string" });

        return JSON.parse(decompressed) as number[][][];
  }, [compressedIterations]);

  console.log(decompressedIterations);

  const runSimulation = useMutation({
    mutationFn: () =>
      httpClient.post(`/simulations/${simulationId}/run`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulations", simulationId] });
    },
  });

  const onRunSimulation = async () => {
    const mutation = runSimulation.mutateAsync();
    toast.promise(mutation, {
      loading: "Running simulation...",
      success: `Simulation ${data!.name} has run successfully!`,
      error: (error) => {
        const message = error.response?.data?.detail;
        return message ?? `Error running simulation ${data!.name}`;
      },
    });
  };

  const chunks = useRef<Blob[]>([]);

  const [isRecording, setIsRecording] = useState(false);

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

  if (isLoading || isFetching) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner size="large" />
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center gap-2">
      {/* {memoizedReactP5Wrapper} */}
      <div className="w-1/3 space-y-4">
        <p>{data?.name}</p>
        <Button
          className="w-1/2"
          onClick={() => onRunSimulation()}
          disabled={runSimulation.isPending}
          >Run simulation</Button>
        <Button
          className="w-1/2"
          disabled={true}
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
        {/* Print the 3d Array */}
        <div className="space-y-4">{decompressedIterations && decompressedIterations.map((iteration, index) => (
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
                            cell === 1 && "bg-blue-500",
                            cell === 2 && "bg-green-500",
                            cell === 3 && "bg-red-500",
                            cell === 4 && "bg-purple-500",
                            cell === 5 && "bg-pink-500",
                            cell === 0 && "bg-gray-200",
                            cell > 200 && "bg-yellow-500"
                          )}
                        />
                      ))}
                    </div>
                  ))}
                </div>
              </div>
        ))}
        </div>
      </div>
    </div>
  );
}
