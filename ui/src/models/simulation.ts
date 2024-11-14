import { SimulationForm } from "@/lib/utils";

export type Simulation = {
  id: string;
  created_at: Date;
  updated_at: Date;
} & SimulationForm;
