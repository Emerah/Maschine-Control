#
# maschine / ableton
# maschine_drums.py
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

from ableton.v2.base.event import listens
from ableton.v2.base.live_api_utils import liveobj_valid
from ableton.v2.control_surface.components.drum_group import DrumGroupComponent
from ableton.v2.control_surface.control.button import PlayableControl


PADS_PER_ROW = 4
COMPLETE_QUADRANTS_RANGE = xrange(4, 116)
MAX_QUADRANT_INDEX = 7
NUM_PADS = 16


class PadMixin(object):
    __module__ = __name__

    def set_matrix(self, matrix):
        super(PadMixin, self).set_matrix(matrix)
        for button in self.matrix:
            button.set_mode(PlayableControl.Mode.playable_and_listenable)
            button.pressed_color = 'DrumGroup.NotePressed'

    # def _on_matrix_pressed(self, button):
    #     pass

    def _on_matrix_released(self, button):
        self._set_control_pads_from_script(False)
        self._update_button_color(button)


class MaschineDrumRack(PadMixin, DrumGroupComponent):

    def __init__(self, translation_channel=None, * a, **k):
        super(MaschineDrumRack, self).__init__(translation_channel=translation_channel, *a, **k)
        self.__on_selected_track_changed.subject = self.song.view
        self.__on_selected_track_changed()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        track = self.song.view.selected_track
        self.__on_devices_changed.subject = track
        if not self._has_drum_rack():
            self._turn_matarix_buttons_off()
        # else:
        #     self._update_led_feedback()

    @listens('devices')
    def __on_devices_changed(self):
        if not self._has_drum_rack():
            self._turn_matarix_buttons_off()
    #     # self._update_led_feedback()

    def _has_drum_rack(self):
        track = self.song.view.selected_track
        if track.has_midi_input and track.devices:
            for device in track.devices:
                if device.can_have_drum_pads:
                    return True
        else:
            return False

    def _update_button_color(self, button):
        if not self._has_drum_rack():
            self._turn_matarix_buttons_off()
        else:
            pad = self._pad_for_button(button)
            color = self._color_for_pad(pad) if liveobj_valid(pad) else 'DrumGroup.PadEmpty'
            if color == 'DrumGroup.PadFilled':
                b_row, _ = button.coordinate
                b_index = (self.matrix.height - b_row - 1) * PADS_PER_ROW
                row_start_note = self._drum_group_device.visible_drum_pads[b_index].note
                pad_quadrant = MAX_QUADRANT_INDEX
                if row_start_note in COMPLETE_QUADRANTS_RANGE:
                    pad_quadrant = (row_start_note - 1) / NUM_PADS
                color = 'DrumGroup.PadQuadrant{}'.format(pad_quadrant)
            button.color = color

    def _turn_matarix_buttons_off(self):
        for button in self.matrix:
            button.color = 'DrumGroup.PadEmpty'

    def _update_control_from_script(self):
        takeover_pads = self._takeover_pads or len(self.pressed_pads) > 0
        mode = PlayableControl.Mode.listenable if takeover_pads else PlayableControl.Mode.playable_and_listenable
        for button in self.matrix:
            button.set_mode(mode)
