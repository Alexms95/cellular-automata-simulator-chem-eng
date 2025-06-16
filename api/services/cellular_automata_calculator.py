import asyncio
from datetime import datetime
from math import floor
from typing import List, Optional, Tuple
from venv import logger

import numpy as np
from domain.schemas import SimulationBase
from services.calculations_helper import (
    SurfaceTypes,
    get_molar_fractions,
    is_component,
    is_intermediate_component,
    is_rotation_component,
    should_execute,
)
from services.movement_analyzer import MovementAnalyzer
from services.reaction_processor import ReactionProcessor
from services.rotation_manager import RotationManager
from services.simulation_state import SimulationState
from utils import calculate_cell_counts


class CellularAutomataCalculator:
    """Main cellular automata calculator"""

    def __init__(
        self,
        simulation: SimulationBase,
        movement_analyzer: MovementAnalyzer,
        reaction_processor: ReactionProcessor,
        rotation_manager: RotationManager,
        simulation_state: SimulationState,
        surface_type: SurfaceTypes = SurfaceTypes.Torus,
    ):
        self.NL = 0
        self.NC = 0
        self.NEMPTY = 0
        self.NCELL = 0
        self.M_iter = np.ndarray
        self.molar_fractions_table: list
        self.simulation = simulation
        self.surface_type = surface_type
        self.EMPTY_FRAC = 0.31  # Fraction of empty cells
        self.__current_progress_percentage = 0.0

        # Auxiliary services
        self.movement_analyzer = movement_analyzer
        self.reaction_processor = reaction_processor
        self.rotation_manager = rotation_manager
        self.simulation_state = simulation_state

    async def calculate_cellular_automata(self):
        """Main method - orchestrates the simulation"""
        # Initialization
        matrix = self._initialize_simulation()

        # Run simulation
        async for progress in self._run_simulation_iterations(matrix):
            yield progress

    def _initialize_simulation(
        self,
    ) -> np.ndarray:
        """Initializes simulation parameters"""
        self.NL = self.simulation.gridHeight
        self.NC = self.simulation.gridLenght

        # Setup surface and cells
        NTOT = self.NC * self.NL
        self.NEMPTY = floor(self.EMPTY_FRAC * NTOT)
        self.NCELL = NTOT - self.NEMPTY

        # Create initial matrix
        matrix = self._create_initial_matrix()

        self._log_simulation_parameters()

        return matrix

    def _create_initial_matrix(self) -> np.ndarray:
        """Creates the initial matrix with random distribution of components"""
        matrix = np.zeros((self.NL, self.NC), dtype=np.int16)
        components = self.simulation.ingredients

        rotation_info = self.rotation_manager.get_rotation_info()

        # Calculate molar fractions and counts
        ci = np.array([comp.molarFraction for comp in components])
        ni = calculate_cell_counts(self.NCELL, ci)

        random_generator = np.random.default_rng()

        # Randomly distribute components
        for i, _ in enumerate(components):
            for _ in range(ni[i]):
                while True:
                    r, c = np.random.randint(0, self.NL), np.random.randint(0, self.NC)
                    if matrix[r, c] == 0:
                        comp_index = i + 1
                        if rotation_info.get("component") == comp_index:
                            comp_index = random_generator.choice(
                                rotation_info.get("states")
                            )

                        matrix[r, c] = comp_index
                        break

        return matrix

    def _log_simulation_parameters(self):
        """Logs simulation parameters"""
        components = self.simulation.ingredients
        component_names = [comp.name for comp in components]
        ci = np.array([comp.molarFraction for comp in components])
        ni = calculate_cell_counts(self.NCELL, ci)

        logger.info(
            "Simulation Inputs:\n"
            f"  Grid Dimensions: Lines={self.NL}, Columns={self.NC}\n"
            f"  Number of Components: NCOMP={len(components)}\n"
            f"  Component Names: {component_names}\n"
            f"  Molar Fractions (Ci): {ci}\n"
            f"  Cell Counts (Ni): {ni}\n"
            f"  Surface Type: {self.surface_type}\n"
            f"  Empty Cells: NEMPTY={self.NEMPTY}\n"
            f"  Occupied Cells: NCELL={self.NCELL}\n"
            f"  Number of Iterations: n_iter={self.simulation.iterationsNumber}"
        )

    async def _run_simulation_iterations(self, matrix: np.ndarray):
        """Runs the simulation iterations"""
        n_iter = self.simulation.iterationsNumber

        state = self.simulation_state

        # Initialize structures for storing results
        self._initialize_result_structures(matrix, n_iter)

        start_time = datetime.now()

        for n in range(1, n_iter + 1):
            state.clear_iteration_state()

            for i in range(self.NL):
                for j in range(self.NC):
                    current_position = (i, j)
                    component = matrix[i, j]

                    if not is_component(component):
                        continue

                    # Process rotation
                    if self._try_process_rotation(matrix, current_position, component):
                        continue

                    # Process reactions
                    if (
                        current_position not in state.reacted_components
                        and not is_rotation_component(component)
                    ):
                        if self._try_process_reactions(
                            matrix, current_position, component
                        ):
                            continue

                    # Process movement
                    if (
                        current_position not in state.moved_components
                        and current_position not in state.reacted_components
                        and not is_intermediate_component(component)
                    ):
                        self._try_process_movement(matrix, current_position, component)

            # Store iteration results
            self._store_iteration_results(
                matrix,
                n,
                len(self.simulation.ingredients),
            )

            # Yield progress updates if percentage changed
            progress_percentage = round(n / n_iter, 2)
            if (
                n % 10 == 0
                and progress_percentage != self.__current_progress_percentage
            ) or n == n_iter:
                self.__current_progress_percentage = progress_percentage
                yield n, n_iter
                await asyncio.sleep(
                    0.01
                )  # Yield control to event loop. It helps to show separate progress updates

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

    def _initialize_result_structures(self, matrix: np.ndarray, n_iter: int):
        """Initializes structures for storing results"""
        self.M_iter = np.zeros((n_iter + 1, self.NL, self.NC), dtype=np.int16)
        self.M_iter[0, :, :] = matrix.copy()

        rotation_info = self.rotation_manager.get_rotation_info()

        molar_fractions_header = (
            ["Iteration"]
            + [comp.name for comp in self.simulation.ingredients]
            + ["Intermediate"]
        )

        self.molar_fractions_table = [
            molar_fractions_header,
            *[None] * (n_iter + 1),  # Placeholder for iteration data
        ]
        self.molar_fractions_table[1] = get_molar_fractions(
            matrix,
            0,
            len(self.simulation.ingredients),
            self.NCELL,
            rotation_info.get("component", None),
        )

    def _try_process_rotation(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        component: int,
    ) -> bool:
        """Processes component rotation and returns if rotation occurred"""
        rotation_info = self.rotation_manager.get_rotation_info()
        if (
            is_rotation_component(component)
            and self.rotation_manager.can_rotate(
                matrix, position, self.surface_type, self.check_constraints
            )
            and should_execute(rotation_info.get("p_rot", 0))
        ):

            self.rotation_manager.rotate_component(matrix, position, component)
            return True
        return False

    def _try_process_reactions(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        component: int,
    ) -> bool:
        """Processes chemical reactions for a component and returns if any reaction occurred"""
        possible_reactions = self.reaction_processor.find_possible_reactions(
            matrix,
            position,
            component,
            self.surface_type,
            self.check_constraints,
            self.simulation_state,
        )

        if possible_reactions:
            return self.reaction_processor.select_and_execute_reaction(
                possible_reactions, component, matrix, self.simulation_state
            )
        return False

    def _try_process_movement(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        component: int,
    ):
        """Processes component movement"""
        can_move, target_pos, probability = (
            self.movement_analyzer.analyze_movement_possibility(
                matrix, position, component, self.surface_type, self.check_constraints
            )
        )

        if can_move and should_execute(probability):
            i, j = position
            matrix[target_pos[0], target_pos[1]] = component
            matrix[i, j] = 0
            self.simulation_state.moved_components.add(target_pos)

    def _store_iteration_results(
        self,
        matrix: np.ndarray,
        iteration: int,
        n_comp: int,
    ):
        """Stores results of the current iteration"""
        self.M_iter[iteration, :, :] = matrix.copy()
        self.molar_fractions_table[iteration + 1] = get_molar_fractions(
            matrix,
            iteration,
            n_comp,
            self.NCELL,
            self.rotation_manager.get_rotation_info().get("component", None),
        )

    def check_constraints(
        self, surface_type: SurfaceTypes, r: int, c: int
    ) -> Optional[Tuple[int, int]]:
        if surface_type == SurfaceTypes.Box:
            return (r, c) if 0 <= r < self.NL and 0 <= c < self.NC else None
        if surface_type == SurfaceTypes.Cylinder:
            return (r, c % self.NC) if 0 <= r < self.NL else None
        if surface_type == SurfaceTypes.Torus:
            return (r % self.NL, c % self.NC)

    def get_results(self) -> Tuple[np.ndarray, List[List]]:
        return self.M_iter, self.molar_fractions_table
