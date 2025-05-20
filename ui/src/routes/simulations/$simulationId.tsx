import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import httpClient from "@/lib/httpClient";
import { Simulation } from "@/models/simulation";
import { ReactP5Wrapper, Sketch } from "@p5-wrapper/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ChevronDown, ChevronLeft, ChevronUp, Play } from "lucide-react";
import pako from "pako";
import { useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { lazy, Suspense } from "react";
const SimulationGrid = lazy(() => import("@/components/SimulationGrid"));

export const Route = createFileRoute("/simulations/$simulationId")({
  component: () => <SimulationDetail />,
});

function SimulationDetail() {
  const { simulationId } = Route.useParams();
  const queryClient = useQueryClient();

  const { data, isLoading, isFetching } = useQuery<Simulation>({
    queryKey: ["simulations", simulationId],
  });

  useQuery({
    queryKey: ["simulations"],
  });

  const rotation = data?.rotation;

  const {
    data: decompressedIterations,
    isLoading: isDecompressing,
    isFetching: isdecom,
    isRefetching: isredecom,
  } = useQuery({
    queryKey: ["decompressedIterations", simulationId, data?.iterations, data],
    queryFn: () => {
      if (!data?.iterations) {
        return [];
      }
      const binaryString = atob(data!.iterations);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const decompressed = pako.inflate(bytes, { to: "string" });
      return JSON.parse(decompressed) as number[][][];
    },
  });

  const runSimulation = useMutation({
    mutationFn: () => httpClient.post(`/simulations/${simulationId}/run`),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["simulations"],
      });
      queryClient.invalidateQueries({
        queryKey: ["decompressedIterations", simulationId],
      });
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

  const gridRef = useRef<any>(null);

  const scrollToTop = () => {
    gridRef.current?.scrollToItem(0, "start");
  };

  const scrollToBottom = () => {
    gridRef.current?.scrollToItem((decompressedIterations?.length ?? 0) - 1 || 0, "start");
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

  if (isDecompressing || isdecom || isredecom) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <Spinner size="large" />
        <span className="text-lg">Loading iterations...</span>
      </div>
    );
  }

  return (
    <div className="flex-flex-col">
      <div className="flex justify-between">
        <Link to="/simulations" className="">
          <Button variant="outline" className="flex items-center gap-2">
            <ChevronLeft className="h-4 w-4" />
            Back to Simulations
          </Button>
        </Link>
        <h1 className="text-xl text-center font-bold mb-4">{data?.name}</h1>
        <Button
          className="flex items-center justify-center gap-2"
          onClick={() => onRunSimulation()}
          disabled={runSimulation.isPending}
        >
          <Play className="h-4 w-4" />
          Run simulation
        </Button>

        {/* Legend Section */}
        {(decompressedIterations?.length ?? 0) > 0 && (
          <div className="w-1/6 fixed bottom-28 left-8 bg-white p-4 rounded-lg border shadow-sm">
            <h3 className="font-semibold mb-4">Legend</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-gray-200" />
                <span>Empty</span>
              </div>
              {data?.reactions?.some((r) => r.hasIntermediate) && (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-500" />
                  <span>Intermediate</span>
                </div>
              )}
              {data?.ingredients.map((ingredient, index) => {
                if (String.fromCharCode(65 + index) === rotation?.component) {
                  return (
                    <div key={index} className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-gradient-to-b from-amber-800 from-50% to-pink-200 to-50%" />
                      <span>{ingredient.name}</span>
                    </div>
                  );
                }
                return (
                  <div key={index} className="flex items-center gap-2">
                    <div className={`w-4 h-4 bg-${ingredient.color}-500`} />
                    <span>{ingredient.name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
      <div className="space-y-4">
        {/* Disabled for now
        <Button className="w-1/2" disabled={true} onClick={generateVideo}>
          {isRecording ? (
            <Spinner size="small">
              <span className="ml-2">Running simulation...</span>
            </Spinner>
          ) : (
            "Generate mp4 video"
          )}
        </Button>
        */}

        {/* Navigation Controls */}
        <div className="fixed bottom-10 right-20 space-x-8 z-50">
          <Button
            variant="secondary"
            size="icon"
            onClick={scrollToTop}
            className="rounded-full shadow-md"
          >
            <ChevronUp className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={scrollToBottom}
            className="rounded-full shadow-md"
          >
            <ChevronDown className="h-4 w-4" />
          </Button>
        </div>

        {/* Print the 3d Array */}
        <Suspense
          fallback={
            <div className="flex flex-col items-center justify-center h-screen gap-4">
              <Spinner size="large" />
              <span className="text-lg">Rendering simulation...</span>
            </div>
          }
        >
          {(decompressedIterations?.length ?? 0) > 0 ? (
            <SimulationGrid
              ref={gridRef}
              iterations={decompressedIterations ?? []}
              ingredients={data?.ingredients ?? []}
              rotationComponent={data?.rotation?.component}
              reactions={data?.reactions}
            />
          ) : (
            <div className="flex flex-col justify-center h-[70vh]">
              <h1 className="text-2xl font-bold text-gray-500">
                Run the simulation to see the results
              </h1>
            </div>
          )}
        </Suspense>
      </div>
    </div>
  );
}
