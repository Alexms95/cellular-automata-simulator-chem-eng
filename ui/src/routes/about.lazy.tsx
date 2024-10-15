import { createLazyFileRoute, Link } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/about")({
  component: About,
});

function About() {
  return (
    <div className="flex flex-col">
      <h1 className="scroll-m-20 text-lg font-extrabold tracking-tight lg:text-xl">
        CELLULAR AUTOMATA SIMULATOR
      </h1>
      <div className="space-y-4 w-full flex flex-col">
        <h2 className="text-lg font-bold">About</h2>
        <p>
          Cellular automata are a class of models that are used to simulate
          complex systems. They are made up of a grid of cells, each of which
          can be in one of a finite number of states. The state of each cell
          changes over time according to a set of rules that determine how the
          state of a cell depends on the states of its neighbors.
        </p>
        <p>
          This simulator allows you to create and run your own cellular automata
          simulations. You can choose the size of the grid, the number of states
          each cell can be in, and the rules that determine how the state of a
          cell changes over time.
        </p>
        <p>
          To get started, go to the <Link className="text-blue-600" to="/">Simulations</Link> page and click on the "New Simulation" button.
        </p>
      </div>
    </div>
  );
}
