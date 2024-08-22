from typing import List, Set, Callable, Tuple
import functools



class Cell:
    value: int
    shadowValue: int
    location: Tuple[int]
    constraints : List[Callable]
    potential_values : Set[int]
    sudoku_size: int
    def __init__(self, sudoku_size: int, location: Tuple[int], value : int=None) -> None:
        self.value : int = value
        self.shadowValue : int = value
        self.potential_values = set(range(1, sudoku_size+1)) # Add all values to potential values
        self.constraints = []
        self.location = location
        self.sudoku_size = sudoku_size
        pass
    def __str__(self) -> str:
        if self.value == None:
            return " "
        return str(self.value)
    def __key(self) -> Tuple[int]:
        return self.location
    def __hash__(self) -> int:
        return hash(self.__key())
    
    def __int__(self):
        return int(self.value)
    def setValue(self, value: int):
        assert value <= self.sudoku_size, "Cannot assign a cell a value bigger than {}.".format(self.sudoku_size)
        assert value >= 0, "Cannot assign a cell a negative value ({}).".format(value)
        if value == 0:
            value = None
        if self.value != value:
            self.value = int(value)
            self.shadowValue = int(value)
    def add_neq_constraint(self, other_cell):
        self.constraints.append(lambda test_value : other_cell != test_value)
        pass
    def evaluateConstraints(self):
        if self.value != None: # If the cell is already solved, don't evaluate anything
            return
        for c in self.constraints:
            for p in self.potential_values.copy():
                if c(p) != True: # If the constraint is not respected with the test value, discard it from potential values
                    self.potential_values.discard(p)
                    print("Disacred potential value {} from cell {}".format(p, self.location))
        
        if len(self.potential_values) == 1:
            self.value = self.potential_values[0]
        if len(self.potential_values) == 0:
            raise ArithmeticError("No more potential values for this cell. We are stuck.")
        pass

    def __eq__(self, other: object) -> bool:
        # This does not tell you whether two cells are the same. This tells you whether their value is the same.
        if other == None:
            return self.value == None
        if self.value == None:
            return False
    
        if isinstance(other, self.__class__):
            if other.value == None:
                return False
            else:
                return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        else:
            raise TypeError("unsupported operand type(s) for ==: '{}' and '{}'").format(self.__class__, type(other))
    
class CellGroup:
    cells: Tuple[Cell]

    def __init__(self, cells: Tuple[Cell]) -> None:
        assert isinstance(cells, Tuple), "First positional argument of a cell group must be Tuple[Cells]. Passed: {}".format(type(cells))
        assert len(cells)>0, "First positional argument of a cell group must be a non-empty Tuple[Cells]. Passed an empty list."
        assert isinstance(cells[0], Cell), "First positional argument of a cell group must be Tuple[Cells]. Passed a list of {}".format(type(cells[0]))
        self.cells = cells
        self.apply_constraints()
        pass
    
    
    def apply_constraints(self) -> None:
        raise NotImplementedError("You should implement this method on a subclass of CellGroup")
        

class UniqueRange(CellGroup):
    # Class for groupings of cells in which only one number can exist at any time
    
    def apply_constraints(self) -> None:
        for cell in self.cells:
            other_cells = list(self.cells)
            other_cells.remove(cell)
            for other_cell in other_cells:
                cell.add_neq_constraint(other_cell)
        

class Box(UniqueRange):
  


    
    def __init__(self, cells: List[List[Cell]]) -> None:
        assert len(cells) == len(cells[0]), "Box is not square"
        flat_cells = []
        for i in range(len(cells)):
            for j in range(len(cells)):
                flat_cells.append(cells[i][j])
            
        super().__init__(tuple(flat_cells))
    

    

class Row(UniqueRange):
   

    def __init__(self, cells: List[Cell]) -> None:
        
        super().__init__(cells)

class Column(UniqueRange):
    

    def __init__(self, cells: List[Cell]) -> None:
        
        super().__init__(cells)

        
class TransposableDict:
    def __init__(self):
        self._dict = {}

    def _normalize_key(self, key):
        return tuple(sorted(key))

    def __setitem__(self, key, value):
        normalized_key = self._normalize_key(key)
        self._dict[normalized_key] = value

    def __getitem__(self, key):
        normalized_key = self._normalize_key(key)
        return self._dict[normalized_key]

    def __delitem__(self, key):
        normalized_key = self._normalize_key(key)
        del self._dict[normalized_key]

    def __contains__(self, key):
        normalized_key = self._normalize_key(key)
        return normalized_key in self._dict

    def items(self):
        return self._dict.items()

    def __repr__(self):
        return repr(self._dict)

class Constraints:
    constraints_by_cell_pair: TransposableDict[(Cell, Cell)]
    def __init__(self) -> None:
        self.constraints_by_cell_pair = TransposableDict()
        

class Grid:
    
    sudoku_size: int
    grid: Tuple[Tuple[Cell]]
    columns : List[Column] = list()
    rows : List[Row] = list()    
    boxes : List[Box] = list()
    constraints : Constraints
    

    def __init__(self, sudoku_size=9) -> None:
        assert sudoku_size % 3 == 0, "Invalid sudoku size"
        self.sudoku_size = sudoku_size
        box_size = int(sudoku_size /3)
        self.grid = tuple([tuple([Cell(sudoku_size, (x,y)) for x in range(sudoku_size)]) for y in range(sudoku_size)])
        self.tgrid = tuple(zip(*self.grid))
        for i in range(sudoku_size):
            self.rows.append(Row(self.grid[i]))        
            self.columns.append(Column(self.tgrid[i]))
        for i in range(box_size):
            for j in range(box_size):
            
                cells = tuple([tuple([self.grid[x][y] for x in range(i*box_size, i*box_size+box_size)] )for y in range(j*box_size, j*box_size+box_size)])

                self.boxes.append(Box(cells)) 
        
        
        pass
    def applyBasicConstraints(self):
        # Box constraints
        pass
    def evaluateAllCellsOnce(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid)):
                self.grid[i][j].evaluateConstraints()


    def __getitem__(self, index) -> Cell:
        return self.grid[index]

    def updateGrid(self, newGrid: List[List[int]]):
        assert(len(self.grid) == len(newGrid)), "Incorrect new grid length when trying to update the grid model"
        for i in range(len(self.grid)):
            for j in range(len(self.grid)):
                if self.grid[i][j] != newGrid[i][j]:
                    print("New cell change")
                    self.grid[i][j].setValue(newGrid[i][j])
                    self.evaluateAllCellsOnce()

    def __str__(self) -> str:
        gridStr = ""
        for row in self.grid:
            gridStr += ("-"*(self.sudoku_size*4))
            gridStr += "\n"
            for cell in row:
                cellFormat = "|  {}".format(cell) 
                gridStr += cellFormat
            gridStr+="|\n"
        gridStr += ("-"*(self.sudoku_size*4))
        return gridStr
            


if __name__ == "__main__":
    grid = Grid()
    
    print(grid)
