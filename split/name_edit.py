from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QVBoxLayout


class EditNameDialog(QDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Name")

        # Layout
        layout = QVBoxLayout(self)

        # Name input
        self.name_input = QLineEdit(name)
        layout.addWidget(self.name_input)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self):
        return self.name_input.text()
