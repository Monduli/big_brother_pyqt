# Last updated 2/15/2024

import sys

from game import BigBrother as bb
from game_v1 import BigBrother as bb1
from game_v2 import BigBrother as bb2
from PyQt5.QtWidgets import QApplication


def main(VERSION=1):
    app = QApplication(sys.argv)
    if VERSION == 1:
        ex = bb()
    elif VERSION == 2:
        ex = bb1()
    elif VERSION == 3:
        ex = bb2()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
