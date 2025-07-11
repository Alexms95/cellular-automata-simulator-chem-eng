import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import httpClient from "@/lib/httpClient";
import { Simulation } from "@/models/simulation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ChevronDown,
  ChevronLeft,
  ChevronUp,
  Download,
  Play,
} from "lucide-react";
import pako from "pako";
import { useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { EditSimulation } from "@/components/editSimulation";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Iterations } from "@/models/iterations";
import { lazy, Suspense } from "react";
const SimulationGrid = lazy(() => import("@/components/SimulationGrid"));

const API_URL = import.meta.env.VITE_API_URL;

export const Route = createFileRoute("/simulations/$simulationId")({
  component: () => <SimulationDetail />,
});

function SimulationDetail() {
  const { simulationId } = Route.useParams();
  const queryClient = useQueryClient();

  const { data, isLoading, isFetching } = useQuery<Simulation>({
    queryKey: ["simulations", simulationId],
  });

  const [chunkNumber, setChunkNumber] = useState(1);

  const { data: iterations, isLoading: isLoadingIterations, isFetching: isFetchingIterations } = useQuery<Iterations>({
    queryKey: ["iterations", simulationId, chunkNumber],
    queryFn: async () => {
      const response = await httpClient.get("/iterations", {
        params: {
          simulation_id: simulationId,
          chunk_number: chunkNumber - 1,
        },
      });
      return response.data;
    },
    enabled: !!simulationId,
  });

  const rotation = data?.rotation;

  const {
    data: decompressedIterations,
    isLoading: isDecompressing,
    isFetching: isdecom,
    isRefetching: isredecom,
  } = useQuery({
    queryKey: [
      "decompressedIterations",
      simulationId,
      iterations,
      iterations?.data,
    ],
    queryFn: () => {
      if (!iterations?.data) {
        return [];
      }
      const binaryString = atob(iterations.data);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const decompressed = pako.inflate(bytes, { to: "string" });
      return JSON.parse(decompressed) as number[][][];
    },
  });

  const [isRunning, setIsRunning] = useState(false);

  const gridRef = useRef<any>(null);

  const simulationGridMemo = useMemo(() => {
    console.log("Rendering SimulationGrid");
    if (areIterationsLoading()) {
      return (
        <div className="flex flex-col items-center justify-center h-screen gap-4">
          <Spinner size="large" className="dark:text-zinc-100" />
          <span className="text-lg dark:text-zinc-100">Loading simulation...</span>
        </div>
      );
    }
    if (
      !decompressedIterations ||
      decompressedIterations.length === 0 ||
      !data
    ) {
      return (
        <div className="flex flex-col justify-center h-[70vh]">
          <h1 className="text-2xl font-bold text-gray-500">
            Run the simulation to see the results
          </h1>
        </div>
      );
    }
    return (
      <SimulationGrid
        ref={gridRef}
        iterations={decompressedIterations}
        ingredients={data.ingredients}
        reactions={data.reactions}
        currentPage={chunkNumber}
      />
    );
  }, [areIterationsLoading, decompressedIterations, data, chunkNumber]);

  const onRunSimulation = (simulationName?: string) => {
    const eventSource = new EventSource(
      `${API_URL}/simulations/${simulationId}/run`
    );

    setIsRunning(true);

    const name = simulationName || "Simulation";

    const toastId = toast.loading("Starting simulation...");
    eventSource.onmessage = (event) => {
      const data = event.data as string;

      if (data.includes("Simulation completed!")) {
        toast.success(`${name} run successfully!`, { id: toastId });
        eventSource.close();
        queryClient.invalidateQueries({
          queryKey: ["simulations"],
        });
        queryClient.invalidateQueries({
          queryKey: ["decompressedIterations", simulationId],
        });
        queryClient.invalidateQueries({
          queryKey: ["iterations", simulationId],
        });
        setIsRunning(false);
        return;
      }
      else if (data.includes("progress")) {
        const progress = parseFloat(JSON.parse(data).progress) * 100;
        toast.loading(`Running ${name}... ${progress.toFixed()} % completed`, {
          id: toastId,
        });
      }
      else {
        toast.loading(data, {
          id: toastId,
        });
      }
    };

    eventSource.onerror = () => {
      toast.error(`Error running ${name}`, { id: toastId });
      eventSource.close();
      setIsRunning(false);
    };
  };

  const downloadCSV = async () => {
    const promise = (async () => {
      const response = await httpClient.get(
        `${API_URL}/simulations/${simulationId}/results`,
        {
          responseType: "blob",
        }
      );

      const contentDisposition = response.headers["content-disposition"];
      let filename = "file.csv";

      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    })();

    toast.promise(promise, {
      loading: "Downloading CSV file...",
      success: "CSV results file downloaded successfully!",
      error: "Failed to download CSV file",
    });
  };

  const scrollToTop = () => {
    gridRef.current?.scrollToItem(0, "start");
  };

  const scrollToBottom = () => {
    gridRef.current?.scrollToItem(
      (decompressedIterations?.length ?? 0) - 1 || 0,
      "start"
    );
  };

  // if (areIterationsLoading()) {
  //   return (
  //     <div className="flex flex-col items-center justify-center h-screen gap-4">
  //       <Spinner size="large" className="dark:text-zinc-100" />
  //       <span className="text-lg dark:text-zinc-100">Loading iterations...</span>
  //     </div>
  //   );
  // }

  return (
    <div className="flex-flex-col">
      <div className="flex justify-between">
        <Link to="/simulations">
          <Button variant="outline" className="dark:text-zinc-900 dark:bg-white">
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Simulations
          </Button>
        </Link>
        <h1 className="text-xl text-center font-bold mb-4 dark:text-white">{data?.name}</h1>
        <Button
          className="flex items-center justify-center gap-2"
          onClick={() => onRunSimulation(data?.name)}
          disabled={isRunning}
        >
          <Play className="h-4 w-4" />
          Run simulation
        </Button>

        {/* Legend Section */}
        {(decompressedIterations?.length ?? 0) > 0 && (
          <div className="flex flex-col gap-[4vh] fixed top-28 right-8 z-10 w-1/8">
            {data && (
              <EditSimulation
                disabled={isRunning}
                complete={true}
                id={data.id}
              />
            )}
            <Button
              className="flex items-center justify-center gap-2 xl:text-sm text-xs dark:text-zinc-900 dark:bg-white bg-zinc-200 dark:hover:text-zinc-100"
              variant="secondary"
              onClick={() => downloadCSV()}
              disabled={isRunning}
            >
              <Download className="h-4 w-4" />
              Download Results
            </Button>
            <div className="bg-white p-4 rounded-lg border shadow-sm text-xs">
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
            <div className="text-xs flex items-center gap-2">
              <Label className="w-1/2 dark:text-white">Page:</Label>
              <Input
                type="number"
                className="w-1/2 dark:bg-zinc-900 dark:text-white"
                value={chunkNumber}
                onChange={(e) => setChunkNumber(Number(e.target.value))}
                min={1}
                max={
                  data?.iterationsNumber
                    ? (data?.iterationsNumber / 1000).toFixed(0) + 1
                    : 1
                }
              />
            </div>
          </div>
        )}
      </div>
      <div className="space-y-4">

        {/* Navigation Controls */}
        <div className="fixed bottom-10 right-20 space-x-8 z-10">
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
              <Spinner size="large" className="dark:text-zinc-100" />
              <span className="text-lg dark:text-zinc-100">Rendering simulation...</span>
            </div>
          }
        >
          {simulationGridMemo}
        </Suspense>
      </div>
    </div>
  );

  function areIterationsLoading() {
    return isLoading || isFetching || isDecompressing || isdecom || isredecom || isLoadingIterations || isFetchingIterations;
  }
}
