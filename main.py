from UI import SudokuUI
import tkinter as tk
from models import Grid
SUDOKU_SIZE = 9


if __name__ == "__main__":
    initial_grid = Grid(SUDOKU_SIZE)
    initial_grid[3][1].value = 9
    print(f"Value is  {initial_grid[3][1]}")
    root = tk.Tk()
    root.title("Sudoku")
    sudoku_ui = SudokuUI(root, initial_grid)
    root.mainloop()