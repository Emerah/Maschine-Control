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
from ableton.v2.base.util import NamedTuple, clamp, find_if, memoize
from ableton.v2.control_surface.components.playable import PlayableComponent
from ableton.v2.control_surface.components.scroll import ScrollComponent
from ableton.v2.control_surface.control.button import ButtonControl, PlayableControl


MAX_START_NOTE = 108
SHARP_INDICES = (1, 3, 4, 6, 10, 13, 15)

# NOTE_NAMES = (u'C', u'D\u266d', u'D', u'E\u266d', u'E', u'F', u'G\u266d', u'G', u'A\u266d', u'A', u'B\u266d', u'B')
NOTE_NAMES = (u'C', u'Dflat', u'D', u'Eflat', u'E', u'F', u'Gflat', u'G', u'Aflat', u'A', u'Bflat', u'B')


class Scale(NamedTuple):
    __module__ = __name__
    name = ''
    notes = []

    def to_root_note(self, root_note):
        return Scale(name=NOTE_NAMES[root_note], notes=[root_note + x for x in self.notes])

    @memoize
    def scale_for_notes(self, notes):
        return [self.to_root_note(b) for b in notes]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        if isinstance(other, Scale):
            return self.name == other.name and self.notes == other.notes
        return False


SCALES = tuple([Scale(name=x[0], notes=x[1]) for x in Live.Song.get_all_scales_ordered()])


class MaschinePadMixin(object):
    __module__ = __name__

    def set_matrix(self, matrix):
        super(MaschinePadMixin, self).set_matrix(matrix)
        for button in self.matrix:
            button.set_mode(PlayableControl.Mode.playable_and_listenable)
            button.pressed_color = 'Keyboard.NotePressed'

    def _on_matrix_pressed(self, _):
        pass

    def _on_matrix_released(self, button):
        self._update_button_color(button)


class MaschineKeyboard(MaschinePadMixin, PlayableComponent, ScrollComponent):
    __events__ = ('scale', 'root_note')

    next_scale_button = ButtonControl()
    previous_scale_button = ButtonControl()

    def __init__(self, translation_channel, info_display, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineKeyboard, self).__init__(*a, **k)
        self._translation_channel = translation_channel
        self._scale = None
        self._root_note = 0
        self._start_note = self._root_note + 36
        self.__on_selected_track_changed.subject = self.song.view
        self.__on_root_note_changed.subject = self.song
        self.__on_scale_name_changed.subject = self.song
        self.__on_selected_track_changed()
        self._scale = self._get_scale_from_name(self.song.scale_name)

    @next_scale_button.pressed
    def _on_next_scale_button_pressed(self, button):
        self.scroll_scales(1)

    @previous_scale_button.pressed
    def _on_previous_scale_button_pressed(self, button):
        self.scroll_scales(-1)

    def scroll_scales(self, offset):
        if self._scale:
            scale_index = clamp(SCALES.index(self._scale) + offset, 0, len(SCALES))
            self.scale = SCALES[scale_index] or SCALES[0]
            self._update_control_from_script()
            self._update_note_translations()
            self._update_led_feedback()

    @property
    def root_note(self):
        return self.song.root_note

    @root_note.setter
    def root_note(self, root_note):
        self.song.root_note = root_note
        self._root_note = root_note
        self._start_note += root_note

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self._song.scale_name = scale.name
        # self.notify_scale(self._scale)

    @listens('root_note')
    def __on_root_note_changed(self):
        self.notify_root_note(self.song.root_note)

    @listens('scale_name')
    def __on_scale_name_changed(self):
        self._scale = self._get_scale_from_name(self.song.scale_name)
        self.notify_scale(self._scale)

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

    def _get_scale_from_name(self, name):
        return find_if(lambda scale: scale.name == name, SCALES) or SCALES[0]

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
            button.color = ('Keyboard.{}').format('Natural' if button.identifier % 12 in self.scale.notes else 'Sharp')

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
        return (inverted_row * self.matrix.width + column + self._start_note + self.root_note, self._translation_channel)

    def _release_all_pads(self):
        for pad in self.matrix:
            if pad.is_pressed:
                pad._release_button()
