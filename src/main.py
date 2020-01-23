import sys
import logging
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication

from pathlib import Path

from src.configuration import Configuration
from src.engine.engine import Engine
from src.interface.top_level_window import TopLevelWindow


def run():
    logging.basicConfig(
        filename='atlas.log', level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    logging.info("Starting Atlas")

    portfolio_file = '/home/istrator/atlas/test/exportfo/exportfo.ini'
    #    if len(sys.argv) > 1:
    #        portfolio_file = sys.argv[1]

    app = QApplication(sys.argv)
    app.setApplicationName('Atlas')
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Button, QColor(128, 128, 00))
    app.setPalette(palette)

    config = Configuration(Path(portfolio_file))
    engine = Engine(config)
    interface = TopLevelWindow(config, engine)

    interface.closeEvent = interface.portfolio_quit
    interface.showMaximized()
    interface.portfolio_open()

    sys.exit(app.exec_())


if __name__ == '__main__':
    run()