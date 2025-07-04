# Cellular Automata Simulation Flowchart

```mermaid
flowchart LR
    %% Entry point
    A([API Route<br>/simulations/$id/run]):::api --> B[SimulationData.run_simulation]:::query
    B --> C[Instantiate<br>CellularAutomataCalculator]:::calc
    C --> D[calculate_cellular_automata]:::calc
    D --> E[_initialize_simulation]:::calc
    E --> F[Create SimulationState]:::state
    F --> G[_run_simulation_iterations]:::calc

    %% Iteration loop
    subgraph Iteration Loop
        direction LR
        I1[Clear iteration state<br>SimulationState.clear_iteration_state]:::state
        PROCESS_CELLS_START[Apply cell rules<br> For each cell in grid]:::loop

        subgraph Process Single Cell
            direction LR
            CELL_ENTRY[Process Next Cell]:::loop
            CELL_ENTRY --> I3{Is valid component?}:::cond
            I3 -->|Yes| I4[_try_process_rotation<br>RotationManager]:::aux
            I4 --> I5{Rotated?}:::cond
            I5 -->|No| I6[_try_process_reactions<br>ReactionProcessor]:::aux
            I6 --> I7{Reacted?}:::cond
            I7 -->|No| I8[_try_process_movement<br>MovementAnalyzer]:::aux
            
            %% Exit points from cell processing
            I3 -->|No| CELL_EXIT[Cell Processed]
            I5 -->|Yes| CELL_EXIT
            I7 -->|Yes| CELL_EXIT
            I8 --> CELL_EXIT
        end

        PROCESS_CELLS_START --> CELL_ENTRY
        CELL_EXIT --> NEXT_CELL_DECISION{More cells in grid?}:::cond
        NEXT_CELL_DECISION -->|Yes| PROCESS_CELLS_START
        NEXT_CELL_DECISION -->|No| I10[Store results<br>_store_iteration_results]:::calc
        I10 --> I11{End of iterations?}:::cond
        I11 -->|No| I1
        I11 -->|Yes| J([Simulation completed<br>Results available]):::api
    end

    G --> I1
    I1 --> PROCESS_CELLS_START

    %% Visual cues for code structure
    classDef api fill:#b3e6ff,stroke:#333,stroke-width:2px;
    classDef query fill:#ffe0b3,stroke:#333,stroke-width:2px;
    classDef calc fill:#e0e0e0,stroke:#333,stroke-width:2px;
    classDef aux fill:#d6f5d6,stroke:#333,stroke-width:1.5px;
    classDef state fill:#f9e6ff,stroke:#333,stroke-width:1.5px;
    classDef cond fill:#fff2cc,stroke:#333,stroke-width:1.5px;
    classDef loop fill:#f2f2f2,stroke:#333,stroke-width:1.5px;

    %% Legend
    subgraph Legend [ ]
        direction LR
        L1([API Layer]):::api
        L2([DB/Query Layer]):::query
        L3([Calculator/Core]):::calc
        L4([Auxiliary: <br>MovementAnalyzer<br>ReactionProcessor<br>RotationManager]):::aux
        L5([SimulationState]):::state
        L6([Condition/Decision]):::cond
        L7([Loop]):::loop
    end
```
