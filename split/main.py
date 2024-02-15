# Last updated 2/15/2024

import sys

from game import BigBrother
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    ex = BigBrother()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
