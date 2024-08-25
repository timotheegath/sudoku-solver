import tkinter as tk
from models import Grid
import string
SUDOKU_SIZE = 9
class SudokuUI:
    alphabet = tuple(list(string.ascii_uppercase))

    def __init__(self, root, grid):
        self.root = root
        self.grid : Grid = grid
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.create_grid()
        self.create_update_button()
        self.create_solve_button()

    def create_grid(self):
        for i in range(9):
            label = tk.Label(self.root, text=f'{self.alphabet[i]}', font=('Arial', 18))
            label.grid(row=i+1, column=0, padx=5, pady=5)
        for j in range(9):
            label = tk.Label(self.root, text=f'{j+1}', font=('Arial', 18))
            label.grid(row=0, column=j+1, padx=5, pady=5)
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.root, width=3, font=('Arial', 18), justify='center')
                entry.grid(row=i+1, column=j+1, padx=5, pady=5)
                if not self.grid[i][j].isEmpty():
                    entry.insert(0, self.grid[i][j])
                    entry.config(state='disabled')
                self.entries[i][j] = entry

    def create_update_button(self):
        update_button = tk.Button(self.root, text="Update Grid", command=self.update_grid)
        update_button.grid(row=10, column=4, pady=10)
    
    def create_solve_button(self):
        solve_button = tk.Button(self.root, text="Solve Grid", command=self.solve)
        solve_button.grid(row=10, column=3, pady=10)
        self.refresh_grid()
    def solve(self):
        self.grid.evaluateAllCellsOnce()

    def update_grid(self):
        new_grid = self.get_grid()
        print("Updated Grid:")
        for row in new_grid:
            print(row)
        self.grid.updateGrid(new_grid)
        self.refresh_grid()

    def get_grid(self):
        new_grid = [[None for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.entries[i][j].get()
                if value.isdigit():
                    if value == 0:
                        new_grid[i][j] = None
                    else:
                        new_grid[i][j] = int(value)
        return new_grid

    def refresh_grid(self):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')
                entry.delete(0, tk.END)
                if not self.grid[i][j].isEmpty():
                    entry.insert(0, self.grid[i][j])
                    entry.config(state='disabled')

# Example usage
