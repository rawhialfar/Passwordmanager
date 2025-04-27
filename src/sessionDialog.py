from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QEvent

class SessionWarningDialog(QDialog):
    def __init__(self, remaining_time, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session Expiring Soon")
        self.setModal(True)  # Make the dialog modal
        self.remaining_time = remaining_time

        # Create layout and widgets
        self.layout = QVBoxLayout(self)
        self.label = QLabel(f"Your session will expire in {int(self.remaining_time)} seconds. Do you want to extend it?")
        self.layout.addWidget(self.label)

        # Add buttons
        self.extend_button = QPushButton("Extend Session")
        self.logout_button = QPushButton("Log Out Now")
        self.layout.addWidget(self.extend_button)
        self.layout.addWidget(self.logout_button)

        # Connect buttons to slots
        self.extend_button.clicked.connect(self.accept)
        self.logout_button.clicked.connect(self.reject)

        # Start a timer to update the remaining time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_remaining_time)
        self.timer.start(1000)  # Update every second

    def update_remaining_time(self):
        """Update the remaining time in the dialog."""
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.timer.stop()
            self.reject()  # Auto-logout if time runs out
        else:
            self.label.setText(f"Your session will expire in {int(self.remaining_time)} seconds. Do you want to extend it?")