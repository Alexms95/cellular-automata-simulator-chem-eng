import { Button } from "@/components/ui/button";
import { createLazyFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createLazyFileRoute("/about")({
  component: About,
});

function About() {
  const [activeSection, setActiveSection] = useState("overview");

  const sections = [
    { id: "overview", label: "Overview" },
    { id: "what-is-ca", label: "What is Cellular Automata?" },
    { id: "components", label: "Simulation Components" },
    { id: "features", label: "Features" },
    { id: "getting-started", label: "Getting Started" },
  ];

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setActiveSection(id);
  };

  return (
    <div className="flex min-h-screen">
      {/* Side Menu */}
      <div className="w-72 bg-zinc-50 dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 p-6 fixed h-full overflow-auto">
        <div className="mb-8">
          <h3 className="font-bold text-lg mb-1">Documentation</h3>
        </div>
        <nav className="space-y-1">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => scrollToSection(section.id)}
              className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${
                  activeSection === section.id
                    ? "bg-zinc-900 text-white dark:bg-zinc-50 dark:text-zinc-900"
                    : "text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                }`}
            >
              {section.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="ml-72 w-full px-6 py-4">
        <div id="overview">
          <h1 className="scroll-m-20 text-2xl font-extrabold tracking-tight lg:text-3xl mb-6">
            Cellular Automata Simulator
          </h1>

          <section className="space-y-4 mb-8 text-left">
            <h2 className="text-xl font-bold">Overview</h2>
            <p className="text-zinc-700 dark:text-zinc-300">
              This simulator is a powerful tool for chemical engineering
              applications that uses cellular automata to model and visualize
              chemical reactions and molecular movements. It provides an
              intuitive way to understand how chemicals interact and move in a
              controlled environment.
            </p>
          </section>
        </div>

        <div id="what-is-ca">
          <section className="space-y-4 mb-8 text-left">
            <h2 className="text-xl font-bold">What is Cellular Automata?</h2>
            <p className="text-zinc-700 dark:text-zinc-300">
              Cellular Automata is a mathematical model that simulates complex
              systems using a grid of cells. In this simulator:
            </p>
            <ul className="list-disc list-inside space-y-2 text-zinc-700 dark:text-zinc-300 ml-4">
              <li>
                Each cell in the grid can represent different chemical
                components (like A, B, C)
              </li>
              <li>
                The simulation advances in discrete time steps (iterations)
              </li>
              <li>
                Cells interact with their neighbors following specific rules
              </li>
              <li>
                These interactions can represent chemical reactions and
                molecular movements
              </li>
            </ul>
          </section>
        </div>

        <div id="components">
          <section className="space-y-4 mb-8 text-left">
            <h2 className="text-xl font-bold">Simulation Components</h2>

            <div className="space-y-3">
              <h3 className="text-lg font-semibold">1. Grid Environment</h3>
              <p className="text-zinc-700 dark:text-zinc-300">
                Create a customizable grid where your simulation takes place:
              </p>
              <ul className="list-disc list-inside ml-4 text-zinc-700 dark:text-zinc-300">
                <li>Define grid dimensions (height × length)</li>
                <li>Each cell can hold different chemical components</li>
                <li>
                  Visual representation with color-coding for each component
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-semibold">2. Chemical Components</h3>
              <p className="text-zinc-700 dark:text-zinc-300">
                Configure your chemical components with:
              </p>
              <ul className="list-disc list-inside ml-4 text-zinc-700 dark:text-zinc-300">
                <li>
                  Custom names and distinctive colors for easy visualization
                </li>
                <li>Initial molar fractions (distribution in the grid)</li>
                <li>
                  Movement probability (PM) controlling how likely a component
                  is to move
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-semibold">3. Chemical Reactions</h3>
              <p className="text-zinc-700 dark:text-zinc-300">
                Model complex chemical reactions:
              </p>
              <ul className="list-disc list-inside ml-4 text-zinc-700 dark:text-zinc-300">
                <li>Define multiple reactants and products</li>
                <li>Include intermediate compounds for complex reactions</li>
                <li>
                  Set forward reaction probabilities (Pr) for reaction
                  occurrence
                </li>
                <li>
                  Configure reverse reaction probabilities for equilibrium
                  modeling
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-semibold">
                4. Interaction Parameters
              </h3>
              <p className="text-zinc-700 dark:text-zinc-300">
                Fine-tune molecular interactions:
              </p>
              <ul className="list-disc list-inside ml-4 text-zinc-700 dark:text-zinc-300">
                <li>Set J-parameters for each pair of components</li>
                <li>
                  Control how different molecules interact with each other
                </li>
                <li>Model attraction or repulsion between components</li>
              </ul>
            </div>
          </section>
        </div>

        <div id="features">
          <section className="space-y-4 mb-8 text-left">
            <h2 className="text-xl font-bold">Features</h2>
            <ul className="list-disc list-inside space-y-2 text-zinc-700 dark:text-zinc-300 ml-4">
              <li>
                Real-time visualization of chemical reactions and movements
              </li>
              <li>Save and load simulation configurations</li>
              <li>Export configurations as JSON files for sharing or backup</li>
              <li>
                Create copies of existing simulations for parameter studies
              </li>
              <li>Track simulation progress with iteration counters</li>
            </ul>
          </section>
        </div>

        <div id="getting-started">
          <section className="space-y-4 text-left">
            <h2 className="text-xl font-bold">Getting Started</h2>
            <p className="text-zinc-700 dark:text-zinc-300">
              Ready to create your first simulation? Follow these steps:
            </p>
            <ol className="list-decimal list-inside ml-4 space-y-2 text-zinc-700 dark:text-zinc-300">
              <li>Click "New Simulation" on the Simulations page</li>
              <li>Set up your grid dimensions</li>
              <li>Add chemical components and their properties</li>
              <li>Define reactions between components</li>
              <li>Configure movement and interaction parameters</li>
              <li>Save your simulation and run it to visualize the results</li>
            </ol>
            <div className="mt-4">
              <Button asChild>
                <Link to="/simulations">Go to Simulations</Link>
              </Button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
