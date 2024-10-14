import { Button } from "@/components/ui/button";
import { ReactP5Wrapper, Sketch } from "@p5-wrapper/react";
import { createLazyFileRoute } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createLazyFileRoute("/about")({
  component: About,
});

function About() {
  const [startRecording, setStartRecording] = useState(false);
  const sketch: Sketch = (p5) => {
    let grid: number[][];
    const cols = 10;
    const rows = cols;
    const resolution = 50;
    let recorder: MediaRecorder;
    let chunks: Blob[] = [];
    let isRecording = false;

    p5.setup = () => {
      p5.createCanvas(500, 500);
      p5.frameRate(5);
      grid = createGrid();
    };

    p5.draw = () => {
      if (p5.frameCount === 1) {
        isRecording = true;
        recorder = new MediaRecorder(
          p5.drawingContext.canvas.captureStream(5),
          {
            mimeType: "video/webm",
          }
        );

        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunks.push(e.data);
          }
        };
        recorder.start();
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
      console.log(p5.frameCount);
      if (p5.frameCount >= 30) {
        p5.noLoop();
        if (isRecording) stopRecording();
      }
    };

    p5.updateWithProps = (props) => {
      if (props.startRecording) {
        startRecording();
      }
    };

    function startRecording() {
      chunks = [];
      isRecording = true;
      recorder = new MediaRecorder(p5.drawingContext.canvas.captureStream(5), {
        mimeType: "video/webm",
      });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.start();
    }

    function stopRecording() {
      recorder.stop();

      recorder.onstop = () => {
        isRecording = false;
        const blob = new Blob(chunks, { type: "video/webm" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = "cellular_automata.webm";
        a.click();
        window.URL.revokeObjectURL(url);
      };

      setStartRecording(false);
    }

    function createGrid() {
      return Array.from({ length: rows }).map(() =>
        Array.from({ length: cols }).map(() => Math.floor(p5.random([0, 1])))
      );
    }
  };

  const saveVideo = () => setStartRecording(true);

  return (
    <div className="flex justify-center">
      <ReactP5Wrapper sketch={sketch} startRecording={startRecording} />
      <Button onClick={saveVideo}>Save video</Button>
    </div>
  );
}
