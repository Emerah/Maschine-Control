#
# maschine / ableton
# maschine_extensions.py
#
# created by Ahmed Emerah - (MaXaR)
#
# NI user name: Emerah
# NI: Machine MK3, KK S49 MK2, Komplete 12.
# email: ahmed.emerah@icloud.com
#
# developed using python 2.7.17 on macOS Catalina
# tools: VS Code (Free)
#
from __future__ import absolute_import, print_function, unicode_literals


class MaschineComponentMixin(object):

    """
    this is a mixin object to facilitate access to Live properties that are frequently used
    inside components. also by making these properties listenable, components can define
    observers, to act upon a property value change.

    an object that inherits from this class, must also be a subclass of the EventObject class.
    """

    # todo: turn these properties to listenable properties.

    @property
    def current_view(self):
        return None

    @property
    def borwser_is_open(self):
        return None

    @property
    def selected_track(self):
        return None

    @property
    def selected_device(self):
        return None

    @property
    def appointed_device(self):
        return None

    @property
    def detail_clip(self):
        return None

    @property
    def selected_parameter(self):
        return None

    @property
    def highlighted_clip_slot(self):
        return None

    @property
    def selected_scene(self):
        return None

    @property
    def selected_chain(self):
        return None

    @property
    def selected_drum_pad(self):
        return None

    @property
    def visible_drum_pads(self):
        return None

    @property
    def is_playing(self):
        return None

    @property
    def tempo(self):
        return None
