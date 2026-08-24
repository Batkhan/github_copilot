import random
import tkinter as tk

CELL = 30
COLUMNS = 10
ROWS = 20
WIDTH = COLUMNS * CELL
HEIGHT = ROWS * CELL

# Fall speed configuration
BASE_FALL_SPEED = 700  # milliseconds, increased for slower fall
FALL_SPEED_DECREASE = 60  # milliseconds per level

SHAPES = [
    ([[1, 1, 1, 1]], "cyan"),
    ([[1, 1], [1, 1]], "yellow"),
    ([[0, 1, 0], [1, 1, 1]], "purple"),
    ([[1, 0, 0], [1, 1, 1]], "orange"),
    ([[0, 0, 1], [1, 1, 1]], "blue"),
    ([[0, 1, 1], [1, 1, 0]], "green"),
    ([[1, 1, 0], [0, 1, 1]], "red"),
]

# Scoring system for completed lines
SCORE_TABLE = {
    1: 100,  # Single line
    2: 300,  # Double line
    3: 500,  # Triple line
    4: 800,  # Tetris
}


class Tetris:
    def __init__(self, window):
        self.window = window
        self.window.title("Mini Tetris")
        self.window.resizable(False, False)
        self.canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="#111827", highlightthickness=0)
        self.canvas.pack(padx=12, pady=(12, 8))
        self.score_label = tk.Label(window, text="Score: 0    Lines: 0    Level: 1", font=("Segoe UI", 11, "bold"))
        self.score_label.pack()
        self.help_label = tk.Label(window, text="Left/Right: move   Up: rotate   Down: drop   Space: hard drop   R: restart", font=("Segoe UI", 9))
        self.help_label.pack(pady=(3, 10))
        self.window.bind("<Key>", self.key_pressed)
        self.start_game()
        self.tick()

    def start_game(self):
        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.spawn_piece()
        self.draw()

    def spawn_piece(self):
        shape, color = random.choice(SHAPES)
        self.piece = [row[:] for row in shape]
        self.color = color
        self.piece_row = 0
        self.piece_column = (COLUMNS - len(self.piece[0])) // 2
        if not self.valid_position(self.piece, self.piece_row, self.piece_column):
            self.game_over = True

    def valid_position(self, shape, row, column):
        for shape_row, cells in enumerate(shape):
            for shape_column, filled in enumerate(cells):
                if not filled:
                    continue
                board_row = row + shape_row
                board_column = column + shape_column
                if board_column < 0 or board_column >= COLUMNS or board_row >= ROWS:
                    return False
                if board_row >= 0 and self.board[board_row][board_column]:
                    return False
        return True

    def move(self, row_change, column_change):
        new_row = self.piece_row + row_change
        new_column = self.piece_column + column_change
        if self.valid_position(self.piece, new_row, new_column):
            self.piece_row = new_row
            self.piece_column = new_column
            self.draw()
            return True
        return False

    def rotate(self):
        rotated = [list(row) for row in zip(*self.piece[::-1])]
        if self.valid_position(rotated, self.piece_row, self.piece_column):
            self.piece = rotated
            self.draw()

    def lock_piece(self):
        for shape_row, cells in enumerate(self.piece):
            for shape_column, filled in enumerate(cells):
                board_row = self.piece_row + shape_row
                board_column = self.piece_column + shape_column
                if filled and board_row >= 0:
                    self.board[board_row][board_column] = self.color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        remaining = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(remaining)
        if cleared:
            self.board = [[None for _ in range(COLUMNS)] for _ in range(cleared)] + remaining
            self.lines += cleared
            # Use the score table for line completion bonuses
            score_multiplier = SCORE_TABLE.get(cleared, 0)
            self.score += score_multiplier * self.level

    @property
    def level(self):
        return self.lines // 10 + 1

    def hard_drop(self):
        distance = 0
        while self.move(1, 0):
            distance += 1
        self.score += distance * 2
        self.lock_piece()
        self.draw()

    def tick(self):
        if not self.game_over and not self.paused:
            if not self.move(1, 0):
                self.lock_piece()
            self.draw()
        # Slower fall speed: increased base speed and reduced decrease per level
        fall_delay = max(100, BASE_FALL_SPEED - (self.level - 1) * FALL_SPEED_DECREASE)
        self.window.after(fall_delay, self.tick)

    def key_pressed(self, event):
        if event.keysym.lower() == "r":
            self.start_game()
        elif event.keysym.lower() == "p" and not self.game_over:
            self.paused = not self.paused
            self.draw()
        elif self.game_over or self.paused:
            return
        elif event.keysym == "Left":
            self.move(0, -1)
        elif event.keysym == "Right":
            self.move(0, 1)
        elif event.keysym == "Down":
            if not self.move(1, 0):
                self.lock_piece()
            self.score += 1
            self.draw()
        elif event.keysym == "Up":
            self.rotate()
        elif event.keysym == "space":
            self.hard_drop()

    def draw_cell(self, column, row, color):
        x1 = column * CELL + 1
        y1 = row * CELL + 1
        # Add rounded corners effect by using oval shapes at corners
        radius = 4
        self.canvas.create_rectangle(x1 + radius, y1, x1 + CELL - 2 - radius, y1 + CELL - 2, 
                                     fill=color, outline="#0b1220", width=2)
        self.canvas.create_rectangle(x1, y1 + radius, x1 + CELL - 2, y1 + CELL - 2 - radius, 
                                     fill=color, outline="#0b1220", width=2)
        # Add gradient effect using slightly darker shade at edges
        self.canvas.create_rectangle(x1, y1, x1 + CELL - 2, y1 + CELL - 2, 
                                     fill=color, outline="#0b1220", width=2)

    def draw(self):
        self.canvas.delete("all")
        for row in range(ROWS):
            for column in range(COLUMNS):
                self.canvas.create_rectangle(column * CELL, row * CELL, (column + 1) * CELL, (row + 1) * CELL, outline="#273449")
                if self.board[row][column]:
                    self.draw_cell(column, row, self.board[row][column])
        if not self.game_over:
            for shape_row, cells in enumerate(self.piece):
                for shape_column, filled in enumerate(cells):
                    if filled and self.piece_row + shape_row >= 0:
                        self.draw_cell(self.piece_column + shape_column, self.piece_row + shape_row, self.color)
        self.score_label.config(text=f"Score: {self.score}    Lines: {self.lines}    Level: {self.level}")
        if self.paused:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="PAUSED", fill="white", font=("Segoe UI", 24, "bold"))
        elif self.game_over:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 15, text="GAME OVER", fill="white", font=("Segoe UI", 23, "bold"))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 22, text="Press R to restart", fill="#cbd5e1", font=("Segoe UI", 12))


if __name__ == "__main__":
    app = tk.Tk()
    Tetris(app)
    app.mainloop()
