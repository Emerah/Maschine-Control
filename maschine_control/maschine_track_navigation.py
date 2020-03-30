#
# maschine / ableton
# maschine_track_selection.py
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

from ableton.v2.base.dependency import depends
from ableton.v2.base.event import listens
from ableton.v2.base.live_api_utils import liveobj_valid
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.components.scroll import ScrollComponent
from ableton.v2.control_surface.components.view_control import BasicTrackScroller
from ableton.v2.control_surface.control.button import ButtonControl


class MaschineTrackNavigator(Component):
    """
    long presses scroll through the track list, short presses will select the next track.
    only the latter option was available when using the track scroller directly.
    """
    track_scroller_type = BasicTrackScroller

    master_track_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.Off')

    @depends(info_display=None)
    def __init__(self, info_display=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineTrackNavigator, self).__init__(*a, **k)
        self._track_scroller = ScrollComponent(self.track_scroller_type(), parent=self)
        song = self.song
        view = song.view
        self.register_slot(song, self.__on_selected_track_changed, 'visible_tracks')
        self.register_slot(song, self.__on_selected_track_changed, 'return_tracks')
        self.register_slot(view, self.__on_selected_track_changed, 'selected_track')
        self.__on_selected_track_changed()
        self._update_master_track_button()

    @property
    def master_track(self):
        return self.song.master_track

    def set_previous_track_button(self, button):
        self._track_scroller.set_scroll_up_button(button)

    def set_next_track_button(self, button):
        self._track_scroller.set_scroll_down_button(button)

    def set_master_track_button(self, button):
        self.master_track_button.set_control_element(button)

    @master_track_button.pressed
    def _on_master_track_button_pressed(self, button):
        self.select_master_track()

    def select_master_track(self):
        selected_track = self.song.view.selected_track
        if selected_track != self.master_track:
            self.song.view.selected_track = self.master_track
        self._update_master_track_button()

    def _update_master_track_button(self):
        selected_track = self.song.view.selected_track
        self.master_track_button.color = 'DefaultButton.On' if selected_track == self.master_track else 'DefaultButton.Off'

    def __on_selected_track_changed(self):
        track = self.song.view.selected_track
        if liveobj_valid(track):
            if self.is_enabled():
                self._track_scroller.update()
        self.__on_name_changed.subject = track
        self._update_master_track_button()
        self._display_track_name(track)
        if not track.devices:
            self._info_display.clear_display(1)
            self._info_display.clear_display(3)

    @listens('name')
    def __on_name_changed(self):
        track = self.song.view.selected_track
        self._display_track_name(track)

    def _display_track_name(self, track):
        if track in self.song.visible_tracks:
            self._info_display.display_message_on_maschine('Track - {} '.format(track.name), 2)
        elif track in self.song.return_tracks:
            self._info_display.display_message_on_maschine('Return - {}'.format(track.name), 2)
        else:
            self._info_display.display_message_on_maschine('Master Track Selected', 2)
