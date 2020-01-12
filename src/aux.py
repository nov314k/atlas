import sys
import logging
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication

from pathlib import Path

from configuration import Configuration
from engine.engine import Engine
from interface.top_level_window import TopLevelWindow
from driver import Driver

def run():
    logging.basicConfig(
            filename='atlas.log', level=logging.DEBUG,
            format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    logging.info("Starting Atlas")
    portfolio_file = 'example-portfolio/example.json'
    if len(sys.argv) > 1:
        portfolio_file = sys.argv[1]

    app = QApplication(sys.argv)
    app.setApplicationName('Atlas')
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Visual sign that I'm working in a different mode
    if len(sys.argv) > 2:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(128, 128, 00))
        app.setPalette(palette)

    config = Configuration(Path(sys.argv[1]))
    engine = Engine(config)
    interface = TopLevelWindow(config, engine)
    driver = Driver(config, interface, engine)

    # TODO I need to pass the correct arguments here!
    interface.closeEvent = interface.portfolio_quit
    interface.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
