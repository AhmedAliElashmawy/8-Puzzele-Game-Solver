import sys, os, time, random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QComboBox, QSlider, QDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QPixmap, QPainter
from algorithm_interface import bfs, dfs, ids, astar

def delete_saved_states(folder_path: str):
    """Delete all files inside the saved states folder.

    This is separated out so it can be tested without launching the GUI.
    """
    try:
        if not os.path.isdir(folder_path):
            return
        for name in os.listdir(folder_path):
            fp = os.path.join(folder_path, name)
            try:
                if os.path.isfile(fp):
                    os.remove(fp)
            except Exception:
                # ignore individual file removal errors
                pass
    except Exception:
        # ignore folder-level errors
        pass


class Tile(QLabel):
    """Single movable tile."""
    def __init__(self, number, parent_gui=None):
        super().__init__(str(number) if number != 0 else "")
        self.number = number
        self.parent_gui = parent_gui
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.update_style()

    def update_style(self):
        if self.number == 0:
            self.setStyleSheet("background-color: #393e46; border-radius: 10px;")
        else:
            self.setStyleSheet("background-color: #00adb5; color: white; border-radius: 10px;")

    def mousePressEvent(self, event):
        """Handle click to cycle tile number."""
        if self.parent_gui:
            # Cycle to next number (0-8)
            self.number = (self.number + 1) % 9
            self.setText(str(self.number) if self.number != 0 else "")
            self.update_style()
            # Update the start_state in parent GUI
            self.parent_gui.update_start_state_from_tiles()
        super().mousePressEvent(event)


class PuzzleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver")
        self.resize(400, 600)
        self.setStyleSheet("background-color: #222831; color: white;")

        self.start_state = (1,2,5,3,4,0,6,7,8)
        self.goal_state = (0, 1, 2, 3, 4, 5, 6, 7, 8)

        self.tiles = {}
        self.path = []
        self.moves = []
        self.stats = QLabel("")
        self.current_step = 0
        self.speed = 50  # milliseconds
        self.tile_size = 100
        self.save_folder = "saved_states"
        self.results_folder = "results"
        os.makedirs(self.save_folder, exist_ok=True)
        os.makedirs(self.results_folder, exist_ok=True)

        self.build_ui()
        self.update_board(self.start_state)

    # ----------------------------- UI -----------------------------
    def build_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title = QLabel("8-Puzzle Solver")
        self.title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        # Puzzle Area (absolute positioning for smooth animation)
        self.board = QWidget()
        self.board.setFixedSize(3 * self.tile_size, 3 * self.tile_size)
        self.board.setStyleSheet("background-color: #222831;")
        layout.addWidget(self.board, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create tiles (QLabels)
        for i, val in enumerate(self.start_state):
            r, c = divmod(i, 3)
            tile = Tile(val, parent_gui=self)
            tile.setParent(self.board)
            tile.setFixedSize(self.tile_size - 10, self.tile_size - 10)
            tile.move(c * self.tile_size, r * self.tile_size)
            self.tiles[val] = tile

        # Random button with checkbox
        random_layout = QHBoxLayout()
        random_layout.setContentsMargins(0, 50, 0, 10)
        random_button = QPushButton("Random")
        random_button.clicked.connect(self.randomize_state)
        random_layout.addWidget(random_button)
        
        self.save_results_checkbox = QCheckBox("Save Results")
        self.save_results_checkbox.setStyleSheet("color: white;")
        random_layout.addWidget(self.save_results_checkbox)
        
        layout.addLayout(random_layout)

        # Controls
        controls = QHBoxLayout()
        self.alg_select = QComboBox()
        self.alg_select.addItems(["BFS", "DFS", "IDS", "A* (Manhattan)", "A* (Euclidean)"])
        controls.addWidget(self.alg_select)


        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_solver)
        controls.addWidget(self.start_button)
        # Details button, shown after solver finishes
        self.details_button = QPushButton("See Details")
        self.details_button.setVisible(False)
        self.details_button.clicked.connect(self.on_details_clicked)
        controls.addWidget(self.details_button)
        layout.addLayout(controls)

        # Speed slider
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)

        self.setLayout(layout)

    # ----------------------------- Logic -----------------------------
    def update_speed(self, value):
        self.speed = 1100 - (value * 10)

    def update_start_state_from_tiles(self):
        """Update start_state based on current tile positions and numbers."""
        # Build a mapping of position -> tile number
        state_list = [0] * 9
        for tile_num, tile in self.tiles.items():
            # Find which position this tile is at
            x = tile.x()
            y = tile.y()
            col = x // self.tile_size
            row = y // self.tile_size
            pos = row * 3 + col
            state_list[pos] = tile.number
        self.start_state = tuple(state_list)
        print("Updated start_state:", self.start_state)

    def randomize_state(self):
        """Generate a random valid puzzle configuration."""
        # Generate random permutation of 0-8
        self.title.setText("8-Puzzle Solver")
        numbers = list(range(9))
        random.shuffle(numbers)
        # Check if solvable (even number of inversions for solvable puzzle)
        inversions = 0
        for i in range(9):
            for j in range(i + 1, 9):
                if numbers[i] != 0 and numbers[j] != 0 and numbers[i] > numbers[j]:
                    inversions += 1
        # If odd inversions, swap first two non-zero tiles to make it solvable
        if inversions % 2 != 0:
            idx1, idx2 = 0, 1
            if numbers[0] == 0:
                idx1 = 1
                idx2 = 2
            elif numbers[1] == 0:
                idx2 = 2
            numbers[idx1], numbers[idx2] = numbers[idx2], numbers[idx1]
        
        self.start_state = tuple(numbers)
        self.update_board(self.start_state)
        print("Randomized start_state:", self.start_state)

    def update_board(self, state):
        # First, rebuild tiles dictionary with new numbers
        old_tiles = self.tiles.copy()
        self.tiles = {}
        
        for i, val in enumerate(state):
            r, c = divmod(i, 3)
            x, y = c * self.tile_size, r * self.tile_size
            
            # Reuse existing tile widget if possible, just update its number
            if val in old_tiles:
                tile = old_tiles[val]
                tile.number = val
                tile.setText(str(val) if val != 0 else "")
                tile.move(x, y)
                tile.update_style()
            else:
                # Create new tile
                tile = Tile(val, parent_gui=self)
                tile.setParent(self.board)
                tile.setFixedSize(self.tile_size - 10, self.tile_size - 10)
                tile.move(x, y)
            
            self.tiles[val] = tile
        
        QApplication.processEvents()

    def start_solver(self):
        if len(set(self.start_state)) != 9:
            self.title.setText("Error: Duplicate numbers found!")
            QTimer.singleShot(2000, lambda: self.title.setText("8-Puzzle Solver"))
            return
        algo = self.alg_select.currentText()
        QApplication.processEvents()
        # hide details button from previous runs
        try:
            self.details_button.setVisible(False)
        except Exception:
            pass

        if algo == "DFS":
            result = dfs(self.start_state, self.goal_state)
        elif algo == "IDS":
            result = ids(self.start_state, self.goal_state)
        elif algo == "BFS":
            result = bfs(self.start_state, self.goal_state)
        elif algo == "A* (Manhattan)":
            result = astar(self.start_state, self.goal_state, heuristic='manhattan')
        elif algo == "A* (Euclidean)":
            result = astar(self.start_state, self.goal_state, heuristic='euclidean')
        else:
            result = dfs(self.start_state, self.goal_state)
        print("Solver result:", result)

        self.path = result.get("path", [])
        self.moves = result.get("moves", [])
        nodes_count = result.get('nodes', result.get('nodes_expanded', 0))
        if result.get("cost") == -1:
            self.title.setText("Not solvable")
            QTimer.singleShot(2000, lambda: self.title.setText("8-Puzzle Solver"))
        self.stats.setText(
            f"Cost: {result.get('cost', 0)} | Nodes: {nodes_count} | Time: {result.get('time', 0) * 1e3:.3f}ms | Depth: {result.get('search_depth', 0)}"
        )

        # Save results to file if checkbox is checked
        if self.save_results_checkbox.isChecked():
            self.save_results_to_file(algo, result)

        # Don't move any tiles or update the board here; start the animation which will
        # animate tiles in-place. Saving of frames will happen after the animation
        # completes so the visible board isn't changed before animation begins.
        self.animate_solution()

    def save_results_to_file(self, algorithm, result):
        """Save solver results to a text file."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{algorithm.replace(' ', '_').replace('*', 'star')}_{timestamp}.txt"
            filepath = os.path.join(self.results_folder, filename)
            
            with open(filepath, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write(f"8-Puzzle Solver Results\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Algorithm: {algorithm}\n")
                f.write(f"Date/Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"Initial State: {self.start_state}\n")
                f.write(f"Goal State: {self.goal_state}\n\n")
                
                f.write("-" * 60 + "\n")
                f.write("Statistics:\n")
                f.write("-" * 60 + "\n")
                f.write(f"Cost: {result.get('cost', 0)}\n")
                f.write(f"Nodes Expanded: {result.get('nodes', result.get('nodes_expanded', 0))}\n")
                f.write(f"Execution Time: {result.get('time', 0) * 1e3:.3f} ms\n")
                f.write(f"Solution Depth: {result.get('search_depth', 0)}\n\n")
                
                if self.moves:
                    f.write("-" * 60 + "\n")
                    f.write("Solution Moves:\n")
                    f.write("-" * 60 + "\n")
                    for i, move in enumerate(self.moves, 1):
                        f.write(f"Step {i}: {move}\n")
                    f.write("\n")
                
                if self.path:
                    f.write("-" * 60 + "\n")
                    f.write("Solution Path (States):\n")
                    f.write("-" * 60 + "\n")
                    for i, state in enumerate(self.path):
                        f.write(f"Step {i}:\n")
                        # Format state as 3x3 grid
                        for row in range(3):
                            f.write("  ")
                            for col in range(3):
                                val = state[row * 3 + col]
                                f.write(f"{val if val != 0 else ' '} ")
                            f.write("\n")
                        f.write("\n")
                
                f.write("=" * 60 + "\n")
            
            print(f"Results saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving results: {e}")

    # ----------------------------- Animation -----------------------------
    def animate_solution(self):
        self.current_step = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(self.speed)

    def next_step(self):
        if self.current_step >= len(self.path) - 1:
            self.timer.stop()
            # Show the details button so user can save frames and inspect moves
            if len(self.path) > 0:
                self.details_button.setVisible(True)
            return
        old_state = self.path[self.current_step]
        new_state = self.path[self.current_step + 1]
        # update title to show progress
        total = max(len(self.path) - 1, 0)
        self.title.setText(f"Step {self.current_step}/{total}")
        # animate and when finished the board will be snapped to new_state
        self.animate_transition(old_state, new_state)
        # increment step (the animation finished handler will ensure final snap)
        self.current_step += 1

    def animate_transition(self, old_state, new_state):
        """Slide the tile that moved into the blank."""
        old_blank = old_state.index(0)
        new_blank = new_state.index(0)

        # the number that moved into the blank in old_state
        moved_tile_num = old_state[new_blank]
        tile_blank = self.tiles[0]
        tile_moved = self.tiles.get(moved_tile_num)

        r_old, c_old = divmod(old_blank, 3)
        r_new, c_new = divmod(new_blank, 3)

        # Blank animation: from old_blank -> new_blank
        anim_blank = QPropertyAnimation(tile_blank, b"pos")
        anim_blank.setDuration(self.speed)
        anim_blank.setStartValue(QPoint(c_old * self.tile_size, r_old * self.tile_size))
        anim_blank.setEndValue(QPoint(c_new * self.tile_size, r_new * self.tile_size))
        anim_blank.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Moved tile animation: from its old pos (new_blank) -> old_blank
        anim_moved = None
        if tile_moved is not None:
            anim_moved = QPropertyAnimation(tile_moved, b"pos")
            anim_moved.setDuration(self.speed)
            anim_moved.setStartValue(QPoint(c_new * self.tile_size, r_new * self.tile_size))
            anim_moved.setEndValue(QPoint(c_old * self.tile_size, r_old * self.tile_size))
            anim_moved.setEasingCurve(QEasingCurve.Type.InOutQuad)

        group = QParallelAnimationGroup()
        group.addAnimation(anim_blank)
        if anim_moved is not None:
            group.addAnimation(anim_moved)
        group.finished.connect(lambda: self.on_animation_finished(new_state))
        group.start()
        # Keep a reference to avoid GC
        self.animation_group = group
    # group handles both animations (blank + moved tile); nothing else needed here

    def on_animation_finished(self, new_state):
        # Ensure all tiles are in their exact end positions and styles are refreshed
        self.update_board(new_state)
        # Update title to reflect that we've reached the new step
        total = max(len(self.path) - 1, 0)
        # current_step may have already been incremented by next_step
        step = min(self.current_step, total)
        self.title.setText(f"Step {step}/{total}")

    def closeEvent(self, event):
        # Remove saved frames when the user closes the window
        delete_saved_states(self.save_folder)
        # continue normal close
        try:
            super().closeEvent(event)
        except Exception:
            event.accept()

    # ----------------------------- Details Viewer -----------------------------
    def on_details_clicked(self):
        # Launch a dialog that replays the moves and highlights the blank tile moves
        try:
            # Pass the current stats text into the details dialog so the same
            # Cost/Nodes/Time/Depth info is visible there.
            stats_text = self.stats.text() if hasattr(self, 'stats') else None
            dlg = DetailsDialog(self.path, self.moves, tile_size=self.tile_size, parent=self, stats_text=stats_text)
            dlg.exec()
        except Exception as e:
            print("Error opening details dialog:", e)


class DetailsDialog(QDialog):
    """Dialog to render the sequence of states and animate each blank-tile move."""
    def __init__(self, path, moves, tile_size=100, parent=None, stats_text: str = None):
        super().__init__(parent)
        self.setWindowTitle("Solution Details")
        self.path = path or []
        self.moves = moves or []
        self.tile_size = tile_size
        self.current_step = 0
        self.animation_group = None
        # optional solver stats text (Cost/Nodes/Time/Depth)
        self.stats_text = stats_text or ""

        self.setFixedSize(3 * self.tile_size + 40, 3 * self.tile_size + 120)
        self.build_ui()
        if self.path:
            self.update_board(self.path[0])

    def build_ui(self):
        layout = QVBoxLayout()
        # Board area
        self.board = QWidget()
        self.board.setFixedSize(3 * self.tile_size, 3 * self.tile_size)
        self.board.setStyleSheet("background-color: #222831;")
        layout.addWidget(self.board, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create tiles
        self.tiles = {}
        for i in range(9):
            lbl = Tile(i)
            lbl.setParent(self.board)
            lbl.setFixedSize(self.tile_size - 10, self.tile_size - 10)
            self.tiles[i] = lbl
        # Text
        # Stats label (shows solver stats passed from main GUI) — made larger
        self.stats_label = QLabel(self.stats_text)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setWordWrap(True)
        self.stats_label.setFont(QFont("Arial", 12,))
        # Make the label wider/taller so it's more prominent
        self.stats_label.setMinimumWidth(3 * self.tile_size)
        self.stats_label.setFixedHeight(90)
        self.stats_label.setStyleSheet(
            "margin-top: 38px; margin-bottom: 2px; padding: 10px; color: white; background-color: transparent;"
        )
        layout.addWidget(self.stats_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Initialize info label safely (don't index into moves if empty)
        self.info_label = QLabel(self.info_text())
        layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls
        ctrls = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play)
        ctrls.addWidget(self.play_button)
        self.prev_button = QPushButton("Prev")
        self.prev_button.clicked.connect(self.prev_step)
        ctrls.addWidget(self.prev_button)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.manual_next)
        ctrls.addWidget(self.next_button)
        layout.addLayout(ctrls)

        self.setLayout(layout)

    def update_board(self, state):
        for i, val in enumerate(state):
            r, c = divmod(i, 3)
            x, y = c * self.tile_size, r * self.tile_size
            if val in self.tiles:
                self.tiles[val].move(x, y)
                # highlight the blank tile with a border when rendering
                if val == 0:
                    self.tiles[val].setStyleSheet("background-color: #ffd369; border: 3px solid #ff5722; border-radius: 10px;")
                else:
                    self.tiles[val].update_style()
        # Refresh info label (safe) so UI reflects current step/move
        try:
            self.update_info_label()
        except Exception:
            pass
        QApplication.processEvents()

    def info_text(self):
        total = max(len(self.path) - 1, 0)
        move = "-"
        if self.moves and 0 <= self.current_step < len(self.moves):
            move = str(self.moves[self.current_step])
        return f"Step: {self.current_step}/{total} | Move: {move}"

    def update_info_label(self):
        if hasattr(self, 'info_label'):
            self.info_label.setText(self.info_text())

    def play(self):
        # auto-play through path
        if not self.path or len(self.path) <= 1:
            return
        self.current_step = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_next)
        self.timer.start(500)

    def play_next(self):
        if self.current_step >= len(self.path) - 1:
            self.timer.stop()
            return
        old_state = self.path[self.current_step]
        new_state = self.path[self.current_step + 1]
        self.animate_transition(old_state, new_state)
        self.current_step += 1

    def animate_transition(self, old_state, new_state):
        old_blank = old_state.index(0)
        new_blank = new_state.index(0)
        moved_tile_num = old_state[new_blank]

        tile_blank = self.tiles[0]
        tile_moved = self.tiles.get(moved_tile_num)

        r_old, c_old = divmod(old_blank, 3)
        r_new, c_new = divmod(new_blank, 3)

        anim_blank = QPropertyAnimation(tile_blank, b"pos")
        anim_blank.setDuration(350)
        anim_blank.setStartValue(QPoint(c_old * self.tile_size, r_old * self.tile_size))
        anim_blank.setEndValue(QPoint(c_new * self.tile_size, r_new * self.tile_size))
        anim_blank.setEasingCurve(QEasingCurve.Type.InOutQuad)

        anim_moved = None
        if tile_moved is not None:
            anim_moved = QPropertyAnimation(tile_moved, b"pos")
            anim_moved.setDuration(350)
            anim_moved.setStartValue(QPoint(c_new * self.tile_size, r_new * self.tile_size))
            anim_moved.setEndValue(QPoint(c_old * self.tile_size, r_old * self.tile_size))
            anim_moved.setEasingCurve(QEasingCurve.Type.InOutQuad)

        group = QParallelAnimationGroup()
        group.addAnimation(anim_blank)
        if anim_moved is not None:
            group.addAnimation(anim_moved)
        group.finished.connect(lambda: self.on_animation_finished(new_state))
        group.start()
        self.animation_group = group

    def on_animation_finished(self, new_state):
        self.update_board(new_state)

    def manual_next(self):
        if not self.path or self.current_step >= len(self.path) - 1:
            return
        old_state = self.path[self.current_step]
        new_state = self.path[self.current_step + 1]
        self.animate_transition(old_state, new_state)
        self.current_step += 1

    def prev_step(self):
        if not self.path or self.current_step <= 0:
            return
        # move backwards by just snapping to previous state
        self.current_step -= 1
        self.update_board(self.path[self.current_step])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleGUI()
    window.show()
    sys.exit(app.exec())
