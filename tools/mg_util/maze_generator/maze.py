
import random
import math
import copy
import time
from maze_generator.cell import Cell

class Maze(object):
    """Class representing a maze; a 2D grid of Cell objects. Contains functions
    for generating randomly generating the maze as well as for solving the maze."""
    def __init__(self, num_rows, num_cols, cell_size):
        """Constructor function that iniates maze with key attributes and creates grid."""
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.cell_size = cell_size
        self.grid_size = num_rows*num_cols
        self.height = num_rows*cell_size
        self.width = num_cols*cell_size
        self.init_grid = self.generate_grid()

    def generate_grid(self):
        """Function that creates a 2D grid of Cell objects to be the maze."""
        grid = list()

        for i in range(self.num_rows):
            grid.append(list())

            for j in range(self.num_cols):
                grid[i].append(Cell(i, j))

        return grid

    def _find_neighbours(self, cell_row, cell_col):
        """Function that finds all existing and unvisited neighbours of a cell in the
        grid. Return a list of tuples containing indices for the unvisited neighbours."""
        neighbours = list()

        def check_neighbour(row, col):
            # Check that a neighbour exists and that it's not visisted before.
            if (row >= 0 and row < self.num_rows and col >= 0 and col < self.num_cols):
                neighbours.append((row, col))

        check_neighbour(cell_row-1, cell_col)     # Top neighbour
        check_neighbour(cell_row, cell_col+1)     # Right neighbour
        check_neighbour(cell_row+1, cell_col)     # Bottom neighbour
        check_neighbour(cell_row, cell_col-1)     # Left neighbour

        if (len(neighbours) > 0):
            return neighbours

        else:
            return None     # None if no unvisited neighbours found

    def _validate_neighbours_generate(self, neighbour_indices, grid):
        """Function that validates whether a neighbour is unvisited or not. When generating
        the maze, we only want to move to move to unvisited cells (unless we are backtracking)."""
        neigh_list = [n for n in neighbour_indices if not grid[n[0]][n[1]].visited]

        if (len(neigh_list) > 0):
            return neigh_list
        else:
            return None

    def _validate_neighbours_solve(self, neighbour_indices, grid, k, l, k_end, l_end, method = "fancy"):
        """Function that validates wheter a neighbour is unvisited or not and discards the
        neighbours that are inaccessible due to walls between them and the current cell. The
        function implements two methods for choosing next cell; one is 'brute-force' where one
        of the neighbours are chosen randomly. The other is 'fancy' where the next cell is chosen
        based on which neighbour that gives the shortest distance to the final destination."""
        if (method == "fancy"):
            neigh_list = list()
            min_dist_to_target = 100000

            for k_n, l_n in neighbour_indices:
                if (not grid[k_n][l_n].visited
                    and not grid[k][l].is_walls_between(grid[k_n][l_n])):
                    dist_to_target = math.sqrt((k_n - k_end)**2 + (l_n - l_end)**2)

                    if (dist_to_target < min_dist_to_target):
                        min_dist_to_target = dist_to_target
                        min_neigh = (k_n, l_n)

            if ("min_neigh" in locals()):
                neigh_list.append(min_neigh)

        elif (method == "brute-force"):
            neigh_list = [n for n in neighbour_indices if not grid[n[0]][n[1]].visited
                and not grid[k][l].is_walls_between(grid[n[0]][n[1]])]

        if (len(neigh_list) > 0):
            return neigh_list
        else:
            return None

    def _pick_random_entry_exit(self, used_entry_exit = None):
        """Function that picks random coordinates along the maze boundary to represent either
        the entry or exit point of the maze. Makes sure they are not at the same place."""
        rng_entry_exit = used_entry_exit    # Initialize with used value

        # Try until unused location along bounday is found.
        while((rng_entry_exit == used_entry_exit)):
            rng_side = random.randint(0, 3)

            if (rng_side == 0):     # Top side
                rng_entry_exit = (0, random.randint(0, self.num_cols-1))

            elif (rng_side == 2):   # Right side
                rng_entry_exit = (self.num_rows-1, random.randint(0, self.num_cols-1))

            elif (rng_side == 1):   # Bottom side
                rng_entry_exit = (random.randint(0, self.num_rows-1), self.num_cols-1)

            elif (rng_side == 3):   # Left side
                rng_entry_exit = (random.randint(0, self.num_rows-1), 0)

        return rng_entry_exit       # Return entry/exit that is different from exit/entry

    def generate_maze(self, start_coor = (0, 0)):
        """Function that implements the depth-first recursive bactracker maze genrator
        algorithm. Hopefully will return a 2D grid of Cell objects that is the resulting maze."""
        grid = self.generate_grid()
        k_curr, l_curr = start_coor             # Where to start generating
        path = [(k_curr, l_curr)]               # To track path of solution
        grid[k_curr][l_curr].visited = True     # Set initial cell to visited
        visit_counter = 1                       # To count number of visited cells
        visited_cells = list()                  # Stack of visited cells for backtracking

        print("\nGenerating the maze with depth-first search...")
        time_start = time.clock()

        while (visit_counter < self.grid_size):     # While there are unvisited cells
            neighbour_indices = self._find_neighbours(k_curr, l_curr)    # Find neighbour indicies
            neighbour_indices = self._validate_neighbours_generate(neighbour_indices, grid)

            if (neighbour_indices is not None):   # If there are unvisited neighbour cells
                visited_cells.append((k_curr, l_curr))              # Add current cell to stack
                k_next, l_next = random.choice(neighbour_indices)     # Choose random neighbour
                grid[k_curr][l_curr].remove_walls(k_next, l_next)   # Remove walls between neighbours
                grid[k_next][l_next].remove_walls(k_curr, l_curr)   # Remove walls between neighbours
                grid[k_next][l_next].visited = True                 # Move to that neighbour
                k_curr = k_next
                l_curr = l_next
                path.append((k_curr, l_curr))   # Add coordinates to part of generation path
                visit_counter += 1

            elif (len(visited_cells) > 0):  # If there are no unvisited neighbour cells
                k_curr, l_curr = visited_cells.pop()      # Pop previous visited cell (backtracking)
                path.append((k_curr, l_curr))   # Add coordinates to part of generation path

        print("Number of moves performed: {}".format(len(path)))
        print("Execution time for algorithm: {:.4f}".format(time.clock() - time_start))

        entry_coor = self._pick_random_entry_exit(None)     # Entry location cell of maze
        exit_coor = self._pick_random_entry_exit(entry_coor)      # Exit location cell of maze
        grid[entry_coor[0]][entry_coor[1]].set_as_entry_exit("entry",
            self.num_rows-1, self.num_cols-1)
        grid[exit_coor[0]][exit_coor[1]].set_as_entry_exit("exit",
            self.num_rows-1, self.num_cols-1)

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                grid[i][j].visited = False      # Set all cells to unvisited before returning grid

        return grid, entry_coor, exit_coor, path

    def solve_dfs(self, grid, entry_coor, exit_coor, method = "fancy"):
        """Function that implements the depth-first recursive bactracker algorithm for
        solving the maze, i.e. starting at the entry point and searching for the exit.
        The main difference from the generator algorithm is that we can't go through
        walls and thus need to implement a proper path-finding algorithm."""
        k_curr, l_curr = entry_coor             # Where to start searching
        grid[k_curr][l_curr].visited = True     # Set initial cell to visited
        visited_cells = list()                  # Stack of visited cells for backtracking
        path = list()                           # To track path of solution and backtracking cells

        print("\nSolving the maze with depth-first search...")
        time_start = time.clock()

        while ((k_curr, l_curr) != exit_coor):     # While the exit cell has not been encountered
            neighbour_indices = self._find_neighbours(k_curr, l_curr)    # Find neighbour indicies
            neighbour_indices = self._validate_neighbours_solve(neighbour_indices, grid, k_curr,
                l_curr, exit_coor[0], exit_coor[1], method = method)

            if (neighbour_indices is not None):   # If there are unvisited neighbour cells
                visited_cells.append((k_curr, l_curr))              # Add current cell to stack
                path.append(((k_curr, l_curr), False))  # Add coordinates to part of search path
                k_next, l_next = random.choice(neighbour_indices)   # Choose random neighbour
                grid[k_next][l_next].visited = True                 # Move to that neighbour
                k_curr = k_next
                l_curr = l_next

            elif (len(visited_cells) > 0):  # If there are no unvisited neighbour cells
                path.append(((k_curr, l_curr), True))   # Add coordinates to part of search path
                k_curr, l_curr = visited_cells.pop()    # Pop previous visited cell (backtracking)

        path.append(((k_curr, l_curr), False))  # Append final location to path
        print("Number of moves performed: {}".format(len(path)))
        print("Execution time for algorithm: {:.4f}".format(time.clock() - time_start))

        return path

    def solve_bfs(self, grid, entry_coor, exit_coor, method = "brute-force"):
        """Function that implements the breadth-first algorithm for solving the maze. This means that
        for each iteration in the outer loop, the search visits one cell in all possible branches. Then
        moves on to the next level of cells in each branch to continue the search."""
        current_level = [entry_coor]               # Stack of cells at current level of search
        path = list()                              # To track path of solution cell coordinates

        print("\nSolving the maze with breadth-frist search...")
        time_start = time.clock()

        while (True):   # Loop until return statement is encuntered
            next_level = list()

            while (current_level):                      # While still cells left to search on current level
                k_curr, l_curr = current_level.pop(0)   # Search one cell on the current level
                grid[k_curr][l_curr].visited = True     # Mark current cell as visited
                path.append(((k_curr, l_curr), False))  # Append current cell to total search path

                if ((k_curr, l_curr) == exit_coor):     # Exit if current cell is exit cell
                    print("Number of moves performed: {}".format(len(path)))
                    print("Execution time for algorithm: {:.4f}".format(time.clock() - time_start))
                    return path

                neighbour_coors = self._find_neighbours(k_curr, l_curr)    # Find neighbour indicies
                neighbour_coors = self._validate_neighbours_solve(neighbour_coors, grid, k_curr,
                    l_curr, exit_coor[0], exit_coor[1], method = method)   # Find real neighbours

                if (neighbour_coors is not None):
                    for coor in neighbour_coors:
                        next_level.append(coor)     # Add all existing real neighbours to next search level

            for cell in next_level:
                current_level.append(cell)  # Update current_level list with cells for nex search level

    def solve_bidirect_dfs(self, grid, entry_coor, exit_coor, method = "brute-force"):
        """Function that implements a bidirectional depth-first recursive bactracker algorithm for
        solving the maze, i.e. starting at the entry point and exit points where each search searches
        for the other search path. NOTE: THE FUNCTION ENDS IN AN INFINITE LOOP FOR SOME RARE CASES OF
        THE INPUT MAZE. WILL BE FIXED IN FUTURE."""
        print(entry_coor, exit_coor)
        k_curr, l_curr = entry_coor            # Where to start the first search
        p_curr, q_curr = exit_coor             # Where to start the second search
        grid[k_curr][l_curr].visited = True    # Set initial cell to visited
        grid[p_curr][q_curr].visited = True    # Set final cell to visited
        backtrack_kl = list()                  # Stack of visited cells for backtracking
        backtrack_pq = list()                  # Stack of visited cells for backtracking
        path_kl = list()                       # To track path of solution and backtracking cells
        path_pq = list()                       # To track path of solution and backtracking cells

        print("\nSolving the maze with bidirectional depth-first search...")
        time_start = time.clock()

        while (True):   # Loop until return statement is encountered
            neighbours_kl = self._find_neighbours(k_curr, l_curr)    # Find neighbours for first search
            real_neighbours_kl = [neigh for neigh in neighbours_kl if not grid[k_curr][l_curr].is_walls_between(grid[neigh[0]][neigh[1]])]
            neighbours_kl = [neigh for neigh in real_neighbours_kl if not grid[neigh[0]][neigh[1]].visited]

            neighbours_pq = self._find_neighbours(p_curr, q_curr)    # Find neighbours for second search
            real_neighbours_pq = [neigh for neigh in neighbours_pq if not grid[p_curr][q_curr].is_walls_between(grid[neigh[0]][neigh[1]])]
            neighbours_pq = [neigh for neigh in real_neighbours_pq if not grid[neigh[0]][neigh[1]].visited]

            if (len(neighbours_kl) > 0):   # If there are unvisited neighbour cells
                backtrack_kl.append((k_curr, l_curr))              # Add current cell to stack
                path_kl.append(((k_curr, l_curr), False))          # Add coordinates to part of search path
                k_next, l_next = random.choice(neighbours_kl)      # Choose random neighbour
                grid[k_next][l_next].visited = True                # Move to that neighbour
                k_curr = k_next
                l_curr = l_next

            elif (len(backtrack_kl) > 0):                  # If there are no unvisited neighbour cells
                path_kl.append(((k_curr, l_curr), True))   # Add coordinates to part of search path
                k_curr, l_curr = backtrack_kl.pop()        # Pop previous visited cell (backtracking)

            if (len(neighbours_pq) > 0):                        # If there are unvisited neighbour cells
                backtrack_pq.append((p_curr, q_curr))           # Add current cell to stack
                path_pq.append(((p_curr, q_curr), False))       # Add coordinates to part of search path
                p_next, q_next = random.choice(neighbours_pq)   # Choose random neighbour
                grid[p_next][q_next].visited = True             # Move to that neighbour
                p_curr = p_next
                q_curr = q_next

            elif (len(backtrack_pq) > 0):                  # If there are no unvisited neighbour cells
                path_pq.append(((p_curr, q_curr), True))   # Add coordinates to part of search path
                p_curr, q_curr = backtrack_pq.pop()        # Pop previous visited cell (backtracking)

            # Exit loop and return path if any opf the kl neighbours are in path_pq.
            if (any((True for n_kl in real_neighbours_kl if (n_kl, False) in path_pq))):
                path_kl.append(((k_curr, l_curr), False))
                path = [p_el for p_tuple in zip(path_kl, path_pq) for p_el in p_tuple]  # Zip paths
                print("Number of moves performed: {}".format(len(path)))
                print("Execution time for algorithm: {:.4f}".format(time.clock() - time_start))
                return path

            # Exit loop and return path if any opf the pq neighbours are in path_kl.
            elif (any((True for n_pq in real_neighbours_pq if (n_pq, False) in path_kl))):
                path_pq.append(((p_curr, q_curr), False))
                path = [p_el for p_tuple in zip(path_kl, path_pq) for p_el in p_tuple]  # Zip paths
                print("Number of moves performed: {}".format(len(path)))
                print("Execution time for algorithm: {:.4f}".format(time.clock() - time_start))
                return path
