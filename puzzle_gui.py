# puzzle_gui.py
import sys, os, time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QComboBox, QSlider
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QPixmap, QPainter
from puzzle_solver import dfs, ids, bfs, astar

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
    def __init__(self, number):
        super().__init__(str(number) if number != 0 else "")
        self.number = number
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.update_style()

    def update_style(self):
        if self.number == 0:
            self.setStyleSheet("background-color: #393e46; border-radius: 10px;")
        else:
            self.setStyleSheet("background-color: #00adb5; color: white; border-radius: 10px;")


class PuzzleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver (Animated PyQt6)")
        self.resize(400, 550)
        self.setStyleSheet("background-color: #222831; color: white;")

        self.start_state = (1,4,2,6,5,8,7,3,0)
        self.goal_state = (0, 1, 2, 3, 4, 5, 6, 7, 8)

        self.tiles = {}
        self.path = []
        self.current_step = 0
        self.speed = 500  # milliseconds
        self.tile_size = 100
        self.save_folder = "saved_states"
        os.makedirs(self.save_folder, exist_ok=True)

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
            tile = Tile(val)
            tile.setParent(self.board)
            tile.setFixedSize(self.tile_size - 10, self.tile_size - 10)
            tile.move(c * self.tile_size, r * self.tile_size)
            self.tiles[val] = tile

        # Controls
        controls = QHBoxLayout()
        self.alg_select = QComboBox()
        self.alg_select.addItems(["DFS", "IDS", "BFS", "A* (Manhattan)", "A* (Euclidean)"])
        controls.addWidget(self.alg_select)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(100, 1000)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.valueChanged.connect(self.update_speed)
        controls.addWidget(QLabel("Speed"))
        controls.addWidget(self.speed_slider)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_solver)
        controls.addWidget(self.start_button)
        layout.addLayout(controls)

        # Stats Label
        self.stats = QLabel("Ready.")
        self.stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats)
        self.setLayout(layout)

    # ----------------------------- Logic -----------------------------
    def update_speed(self, value):
        self.speed = value

    def update_board(self, state):
        for i, val in enumerate(state):
            r, c = divmod(i, 3)
            x, y = c * self.tile_size, r * self.tile_size
            # move all tiles including the blank (0) so visuals stay in sync
            if val in self.tiles:
                self.tiles[val].move(x, y)
                self.tiles[val].update_style()
        QApplication.processEvents()

    def start_solver(self):
        algo = self.alg_select.currentText()
        self.stats.setText("Solving...")
        QApplication.processEvents()

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

        self.path = result.get("path", [])
        nodes_count = result.get('nodes', result.get('nodes_expanded', 0))
        self.stats.setText(
            f"Cost: {result.get('cost', 0)} | Nodes: {nodes_count} | Time: {result.get('time', 0):.3f}s | Depth: {result.get('depth', 0)}"
        )

        # Don't move any tiles or update the board here; start the animation which will
        # animate tiles in-place. Saving of frames will happen after the animation
        # completes so the visible board isn't changed before animation begins.
        self.animate_solution()

    # ----------------------------- Animation -----------------------------
    def animate_solution(self):
        self.current_step = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(self.speed)

    def next_step(self):
        if self.current_step >= len(self.path) - 1:
            self.timer.stop()
            self.stats.setText(self.stats.text() + " | Animation finished ✅")
            # No animation took place (single-state path) — save frames now
            try:
                self.save_states()
            except Exception:
                pass
            return
        old_state = self.path[self.current_step]
        new_state = self.path[self.current_step + 1]
        # update title to show progress
        total = max(len(self.path) - 1, 0)
        self.title.setText(f"8-Puzzle Solver — Step {self.current_step}/{total}")
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
        self.title.setText(f"8-Puzzle Solver — Step {step}/{total}")
        # If we've reached the final step, save the frames now (after animation)
        if step >= total:
            try:
                self.save_states()
            except Exception:
                pass

    def closeEvent(self, event):
        # Remove saved frames when the user closes the window
        delete_saved_states(self.save_folder)
        # continue normal close
        try:
            super().closeEvent(event)
        except Exception:
            event.accept()

    # ----------------------------- Save States -----------------------------
    def save_states(self):
        # Render and save each step so the saved frames match the animation.
        # Only the tile widgets are drawn onto a transparent pixmap so buttons
        # and other UI elements are excluded.
        for i, state in enumerate(self.path):
            # Update widget positions so tiles are at correct coords
            self.update_board(state)
            QApplication.processEvents()

            # Create a transparent pixmap the size of the board and draw each tile on it
            pixmap = QPixmap(self.board.size())
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            try:
                for val, tile in self.tiles.items():
                    # grab the tile's visual and paint it at its current board-relative position
                    tile_pix = tile.grab()
                    painter.drawPixmap(tile.pos(), tile_pix)
            finally:
                painter.end()

            filename = os.path.join(self.save_folder, f"step_{i:03d}.png")
            pixmap.save(filename)
        print(f"Saved {len(self.path)} frames to '{self.save_folder}'.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleGUI()
    window.show()
    sys.exit(app.exec())
