import "./App.css";
import { SimulationsList } from "./pages/SimulationsList";

function App() {
  return (
    <div className="flex flex-col">
      <h1 className="scroll-m-20 text-lg font-extrabold tracking-tight lg:text-xl">
        CELLULAR AUTOMATA SIMULATOR
      </h1>
      <SimulationsList />
    </div>
  );
}

export default App;
