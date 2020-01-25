"""Docstring."""

from PyQt5.QtGui import QFontDatabase
from pkg_resources import resource_string


DEFAULT_FONT_SIZE = 8
FONT_NAME = 'Source Code Pro'
FONT_FILENAME_PATTERN = 'SourceCodePro-{variant}.otf'
FONT_VARIANTS = ('Bold', 'BoldIt', 'It', 'Regular', 'Semibold', 'SemiboldIt')


class Font:
    """Docstring."""

    _DATABASE = None

    # ~ def __init__(self, color='#181818', paper='#FEFEF7', bold=False,
    # ~ italic=False):
    def __init__(self, bold=False, italic=False):
        """Docstring."""

        # ~ self.color = color
        # ~ self.paper = paper
        self.bold = bold
        self.italic = italic

    @classmethod
    def get_database(cls):
        """Docstring."""

        if cls._DATABASE is None:
            cls._DATABASE = QFontDatabase()
            for variant in FONT_VARIANTS:
                filename = FONT_FILENAME_PATTERN.format(variant=variant)
                # ~ font_data = load_font_data(filename)
                font_data = resource_string('resources', 'fonts/' + filename)
                cls._DATABASE.addApplicationFontFromData(font_data)
        return cls._DATABASE

    def load(self, size=DEFAULT_FONT_SIZE):
        """Docstring."""

        return Font.get_database().font(FONT_NAME, self.stylename, size)

    @property
    def stylename(self):
        """Docstring."""

        if self.bold:
            if self.italic:
                return 'Semibold Italic'
            return 'Semibold'
        if self.italic:
            return 'Italic'
        return 'Regular'
