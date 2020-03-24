#
# native instruments / ableton
# maschine_keyboard.py
#
# created by Ahmed Emerah - (MaXaR)
#
# NI user name: Emerah
# NI: Machine MK3, KK S49 MK2, Komplete 12.
# email: ahmed.emerah@icloud.com
#
# developed using pythons 2.7.17 on macOS Mojave
# tools: VS Code (Free), PyCharm CE (Free)
#
from __future__ import absolute_import, print_function, unicode_literals
import Live  # noqa
from ableton.v2.base.event import listens
from ableton.v2.control_surface.components.playable import PlayableComponent
from ableton.v2.control_surface.components.scroll import ScrollComponent
from ableton.v2.control_surface.control.button import PlayableControl


MAX_START_NOTE = 108
SHARP_INDICES = (1, 3, 4, 6, 10, 13, 15)


class PadMixin(object):
    __module__ = __name__

    def set_matrix(self, matrix):
        super(PadMixin, self).set_matrix(matrix)
        for button in self.matrix:
            button.set_mode(PlayableControl.Mode.playable_and_listenable)
            button.pressed_color = 'Keyboard.NotePressed'

    def _on_matrix_pressed(self, _):
        pass

    def _on_matrix_released(self, button):
        self._update_button_color(button)


class MaschineKeyboard(PadMixin, PlayableComponent, ScrollComponent):

    def __init__(self, translation_channel, *a, **k):
        super(MaschineKeyboard, self).__init__(*a, **k)
        self._translation_channel = translation_channel
        self._start_note = 36
        self.__on_selected_track_changed.subject = self.song.view
        self.__on_selected_track_changed()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        track = self.song.view.selected_track
        self.__on_devices_changed.subject = track
        if not self._has_instrument():
            self._turn_matarix_buttons_off()
        else:
            self._update_led_feedback()

    @listens('devices')
    def __on_devices_changed(self):
        if not self._has_instrument():
            self._turn_matarix_buttons_off()
        else:
            self._update_led_feedback()

    def _has_instrument(self):
        track = self.song.view.selected_track
        if track.has_midi_input and track.devices:
            for device in track.devices:
                if device.type == Live.Device.DeviceType.instrument and not device.can_have_drum_pads:
                    return True
        else:
            return False

    def _update_button_color(self, button):
        if not self._has_instrument():
            self._turn_matarix_buttons_off()
        else:
            button.color = ('Keyboard.{}').format('Sharp' if button.index in SHARP_INDICES else 'Natural')

    def _turn_matarix_buttons_off(self):
        for button in self.matrix:
            button.color = 'DefaultButton.Off'

    def can_scroll_up(self):
        return self._start_note < MAX_START_NOTE

    def can_scroll_down(self):
        return self._start_note > 0

    def scroll_up(self):
        if self.can_scroll_up():
            self._move_start_note(12)

    def scroll_down(self):
        if self.can_scroll_down():
            self._move_start_note(-12)

    def _move_start_note(self, factor):
        self._start_note += factor
        self._update_note_translations()
        self._release_all_pads()

    def _note_translation_for_button(self, button):
        row, column = button.coordinate
        inverted_row = self.matrix.height - row - 1
        return (inverted_row * self.matrix.width + column + self._start_note, self._translation_channel)

    def _release_all_pads(self):
        for pad in self.matrix:
            if pad.is_pressed:
                pad._release_button()
