# ui.py - Главный файл UI, импортирует все панели ригов
# Каждый риг определяется по Custom Property "RigId" на Armature

from . import therig_ui
from . import therigmod_ui
from . import theplush_ui
from . import thesimple_ui
from . import thebuff_ui
from . import thecamera_ui


def register():
    therig_ui.register()
    therigmod_ui.register()
    theplush_ui.register()
    thesimple_ui.register()
    thebuff_ui.register()
    thecamera_ui.register()


def unregister():
    thecamera_ui.unregister()
    thebuff_ui.unregister()
    thesimple_ui.unregister()
    theplush_ui.unregister()
    therigmod_ui.unregister()
    therig_ui.unregister()
