from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QTextEdit


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def appendFormattedText(self, text, formatting):
        default_char_format = QTextCharFormat()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        for line in text.split("\n"):
            for substring, color in formatting.items():
                start = line.find(substring)
                if start != -1:
                    cursor.insertText(line[:start], default_char_format)

                    # Apply color formatting
                    char_format = QTextCharFormat()
                    char_format.setForeground(color)
                    cursor.insertText(substring, char_format)

                    # Remove the colored substring from the line
                    line = line[start + len(substring) :]

                    # Reset to default formatting
                    cursor.insertText(line, default_char_format)
                    line = ""

            cursor.insertText(line, default_char_format)
            cursor.insertText("\n", default_char_format)

        self.setTextCursor(cursor)

    def appendHtml(self, html):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html)
        self.setTextCursor(cursor)

    def appendPlainText(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
