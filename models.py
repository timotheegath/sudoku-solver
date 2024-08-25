from enum import Enum
from typing import List, Set, Callable, Tuple, Dict
import functools
import string

# Constraints
class Constraint:
    # A constraint is a single condition on one cell
    ConstraintTypes = Enum('ConstraintType', ['NEQ', 'EQ'])
    cell: "Cell"
    partnerCell: "Cell"
    type: ConstraintTypes
    def __init__(self, type, cell, partnerCell:"Cell" = None) -> None:
        assert type in self.ConstraintTypes
        if type in (self.ConstraintTypes.EQ, self.ConstraintTypes.NEQ):
            assert partnerCell, "A partner cell must be provided for a constraint of type {}".format(type)
            self.partnerCell = partnerCell
        self.type = type
        self.cell = cell
        
    def evaluateConstraint(self, potentialValue: int):
        # Returns true if constraints is satisfied        
        if self.type == self.ConstraintTypes.EQ:
            
            if self.partnerCell.isEmpty():
                return True
            otherValue = self.partnerCell.value
            return potentialValue==otherValue
        if self.type == self.ConstraintTypes.NEQ:
            
            if self.partnerCell.isEmpty():
                return True
            otherValue = self.partnerCell.value
            return potentialValue!=otherValue
    def __call__(self, potentialValue: int) -> bool:
        return self.evaluateConstraint(potentialValue)
    def __repr__(self) -> str:
        return f"{self.type} constraint on {self.cell!r} linked to {self.partnerCell!r}"



class _CellGroup:
    cells: Tuple["Cell"]
    def __init__(self, cells: Tuple["Cell"]) -> None:
        assert isinstance(cells, Tuple), "First positional argument of a cell group must be Tuple[Cells]. Passed: {}".format(type(cells))
        assert len(cells)>0, "First positional argument of a cell group must be a non-empty Tuple[Cells]. Passed an empty list."
        assert isinstance(cells[0], Cell), "First positional argument of a cell group must be Tuple[Cells]. Passed a list of {}".format(type(cells[0]))
        self.cells = cells
        self.apply_constraints()
        for c in self.cells:
            c._memberOfGroup.append(self)
        pass

    def __hash__(self) -> int:
        return hash(self.cells)*hash(self.__class__)
    def __eq__(self, other_object: object) -> bool:
        if isinstance(other_object, self.__class__):
            return set(self.cells) == set(other_object.cells)
    
    def apply_constraints(self) -> None:
        raise NotImplementedError("You should implement this method on a subclass of CellGroup")
    @staticmethod
    def find_common_groups(*args: "Cell"):
        if any([not isinstance(a, Cell) for a in args]):
            raise TypeError("All arguments must be cells")
        common_group_set = set(args[0].member_of_groups)
        for a in args[1:]:
            common_group_set &= a.member_of_groups
            
        return list(common_group_set)
        

class _UniqueRange(_CellGroup):
    # Class for groupings of cells in which only one number can exist at any time
    # Inherit if you need that constraint
    p_frequencies : Dict
    # Structure is:
    # 1 : [Cell1, Cell3, Cell 5]
    # 2 : [Cell1]
    # etc.. 
    
    def apply_constraints(self) -> None:
        for cell in self.cells:
            other_cells = list(self.cells)
            other_cells.remove(cell)
            for other_cell in other_cells:
                cell.add_neq_constraint(other_cell)
    
    def count_frequency_of_p_values(self) -> None:
        values_dict = {}
        transformed_dict = {}
        for cell in self.cells:
            values_dict[cell] = cell.potential_values
        for key, values in values_dict.items():
            for value in values:
                if value not in transformed_dict:
                    transformed_dict[value] = []
                transformed_dict[value].append(key)
        self.p_frequencies = transformed_dict.copy()
        return transformed_dict
    def claim_cell_value_away_from_other_ranges(self):
        # For instance, where the value 2 can only exist in A1 and A2 for the A row, then the value 2 cannot be anywhere else in that A1-A2-... box top-left.
        self.count_frequency_of_p_values()
        for p_value, cells in self.p_frequencies.items():
            if len(cells) <= 3:
                common_groups = self.find_common_groups(cells)
                common_groups.remove(self)
                for group in common_groups:
                    other_cells_to_clear = [cell for cell in group.cells if cell not in cells]
                    for c in other_cells_to_clear:
                        c.del_potential_value(p_value)
                

        return
    def solveUniqueValuesInRange(self):
        self.count_frequency_of_p_values()
        for p_value, cells in self.p_frequencies.items():
            if len(cells) == 1:
                # If the potential value only exists in this cell, then it must be the cell's value
                cells[0].value = p_value


        

class Box(_UniqueRange):



    
    def __init__(self, cells: List[List["Cell"]]) -> None:
        assert len(cells) == len(cells[0]), "Box is not square"
        flat_cells = []
        for i in range(len(cells)):
            for j in range(len(cells)):
                flat_cells.append(cells[i][j])
            
        super().__init__(tuple(flat_cells))
    def __repr__(self) -> str:
        return f"Box {self.cells[0]._location!r} & {self.cells[1]._location!r}"
    

    

class Row(_UniqueRange):


    def __init__(self, cells: List["Cell"]) -> None:
        self.number = cells[0]._location.x
        super().__init__(cells)
    def __repr__(self) -> str:
        return f"Row {self.number}"

class Column(_UniqueRange):
    

    def __init__(self, cells: List["Cell"]) -> None:
        self.number = cells[0]._location.y
        super().__init__(cells)
    def __repr__(self) -> str:
        return f"Column {self.number}"
        
##########################################
###########################################
# Cell object
class Cell:
    _value: int
    _location: "GridLocation"
    _constraints : Dict
    _potential_values : Set[int]
    _memberOfGroup = []
    sudoku_size: int
    def __init__(self, sudoku_size: int, location: Tuple[int], value : int=None) -> None:
        self._value : int = value
        self._shadowValue : int = value
        self._potential_values = set(range(1, sudoku_size+1)) # Add all values to potential values
        self._constraints = {}
        self._location = GridLocation(*location)
        self.sudoku_size = sudoku_size
        pass
    def __str__(self) -> str:
        if self._value == None:
            return " "
        return f"{self._value}"
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self._location!r}"
    def __key(self) -> int:
        return hash(self._location)
    def __hash__(self) -> int:
        return hash(self.__key())    
    def __int__(self):
        return int(self._value)
    @property
    def value(self):

        return self._value
    
    @value.setter
    def value(self, new_value:int) -> None:
        if new_value > self.sudoku_size:
            raise ValueError("Cannot assign a cell a value bigger than {}.".format(self.sudoku_size))
        if new_value < 0:
            raise ValueError("Cannot assign a cell a negative value ({}).".format(new_value))
        if new_value == 0 or new_value is None:
            self._value = None
            return
        if self._value != new_value:
            if self.allConstraintsHoldWithValue(new_value) and self.is_a_potential_value(new_value):
                #If the value changes
                self._value = int(new_value)
                self._potential_values = set()        
                # The value has changed, so automatically re-evaluate the constraints of partner cells:
                for partnerCell in self._constraints.keys():
                    partnerCell.evaluateConstraints()
                # The potential values have been updated for all the cells in the shared unique range group of this current cell. Check if any cell is the only one with a potential value in the range:
                for group in self._memberOfGroup:
                    group.solveUniqueValuesInRange()
                return
            else:
                print("Incorrect value !")
        
    @property
    def potential_values(self) -> Set[int]:
        return self._potential_values.copy()   
    
    @property
    def member_of_groups(self) -> List[_CellGroup]:
        return self._memberOfGroup

    def add_neq_constraint(self, other_cell):
        if other_cell not in self._constraints.keys():
            self._constraints[other_cell] = []
        self._constraints[other_cell].append(Constraint(Constraint.ConstraintTypes.NEQ, self, other_cell))
        pass
    
  
    
    def evaluateConstraints(self):
        if not self.isEmpty(): # If the cell is already solved, don't evaluate anything
            return
        for p in self._potential_values.copy():
            if not self.allConstraintsHoldWithValue(p): # If the constraint is not respected with the test value, discard it from potential value         
                self.del_potential_value(p)
                print("Discarded potential value {} from cell {}".format(p, self._location))
            
        if len(self._potential_values) == 1:
            self._value = self._potential_values[0]
        if len(self._potential_values) == 0:
            raise ArithmeticError("No more potential values for this cell. We are stuck.")
        pass

    def allConstraintsHoldWithValue(self, test_value):
        if not self.isEmpty(): # If the cell is already solved, don't evaluate anything
            return
        for c_c in self._constraints.values(): #  Returns a list of constraints per Other_cell
            for c in c_c: # Ierate through constraints in Other_cell
                if c(test_value) != True: # If the constraint is not respected with the test value, return False
                    return False
        return True
    def is_a_potential_value(self, test):
        return test in self._potential_values
    def del_potential_value(self, value_to_remove):
        self._potential_values.discard(value_to_remove)
                        
            

    def __eq__(self, other: object) -> bool:
        # This does not tell you whether two cells are the same. This tells you whether their value is the same.
        if other is None:
            return False
        if self.isEmpty():
            return False
    
        if isinstance(other, self.__class__):
            if other.isEmpty():
                return False
            else:
                return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        else:
            raise TypeError("unsupported operand type(s) for ==: '{}' and '{}'").format(self.__class__, type(other))
    def isEmpty(self) -> bool:
        return self._value is None
        
class GridLocation:
    x: int
    y: int
    representation: str
    alphabet = tuple(list(string.ascii_uppercase))
    def __init__(self, x, y) -> None:

        self.x = x
        self.y = y
        self.representation = "{}{}".format(self.alphabet[y], self.x + 1)

    def __str__(self) -> str:
        return self.representation
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x},{self.y})"
    def __hash__(self) -> int:
        return hash((self.x, self.y))
           

class Grid:
    # First index indicates the column: left-to-right
    # Second index indicates the tow: top-to-bottom
    sudoku_size: int
    _grid: Tuple[Tuple[Cell]]
    _uniqueRanges : list[_UniqueRange] = []


    

    def __init__(self, sudoku_size=9) -> None:
        def _build_standard_constraints():
            box_size = int(self.sudoku_size /3)
            self._grid = tuple([tuple([Cell(sudoku_size, (x,y)) for x in range(sudoku_size)]) for y in range(sudoku_size)])
            tgrid = tuple(zip(*self._grid))
            for i in range(sudoku_size):
                self._uniqueRanges.append(Column(self._grid[i]))        
                self._uniqueRanges.append(Row(tgrid[i]))
            for i in range(box_size):
                for j in range(box_size):
                
                    cells = tuple([tuple([self._grid[x][y] for x in range(i*box_size, i*box_size+box_size)] )for y in range(j*box_size, j*box_size+box_size)])

                    self._uniqueRanges.append(Box(cells))     


        assert sudoku_size % 3 == 0, "Invalid sudoku size"
        self.sudoku_size = sudoku_size
        _build_standard_constraints()
        
        
    

    def evaluateAllCellsOnce(self):
        for i in range(len(self._grid)):
            for j in range(len(self._grid)):
                self._grid[i][j].evaluateConstraints()
        for r in self._uniqueRanges:
            r.solveUniqueValuesInRange()
            


    def __getitem__(self, index) -> Cell:
        return self._grid[index]

    def updateGrid(self, newGrid: List[List[int]]):
        assert(len(self._grid) == len(newGrid)), "Incorrect new grid length when trying to update the grid model"
        for i in range(len(self._grid)):
            for j in range(len(self._grid)):
                if newGrid[i][j] is None:
                    continue
                if self._grid[i][j] != newGrid[i][j]:
                    print("New cell change")
                    self._grid[i][j].value = newGrid[i][j]


    def __str__(self) -> str:
        gridStr = ""
        for row in self._grid:
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
