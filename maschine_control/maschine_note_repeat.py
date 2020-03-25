#
# maschine / ableton
# maschine_note_repeat.py
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

from _functools import partial

from ableton.v2.base import task
from ableton.v2.base.event import listens
from ableton.v2.base.util import in_range
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control.button import ButtonControl
from ableton.v2.control_surface.control.control_list import control_list


def _frequency_to_repeat_rate(frequency):
    return 1.0 / frequency * 4.0


NOTE_REPEAT_RATES = map(_frequency_to_repeat_rate, [32*1.5, 32, 16*1.5, 16, 8*1.5, 8, 4*1.5, 4])
DEFAULT_INDEX = 5
DEFAULT_RATE = NOTE_REPEAT_RATES[DEFAULT_INDEX]


class DummyNoteRepeat(object):
    __module__ = __name__
    repeate_rate = 1.0
    enabled = False


class MaschineNoteRepeat(Component):
    """
    this object is an edit of push2 note repeat component.
    object can be en/disabled. the object is not available
    when an audio track is selected. on midi tracks, when
    the object is enabled, a button matrix lights up
    and each button selects one of the available rates.
    """

    __events__ = ('selected_rate_index',)
    select_buttons = control_list(ButtonControl, 8)

    def __init__(self, note_repeat=None, *a, **k):
        super(MaschineNoteRepeat, self).__init__(*a, **k)
        self._note_repeat = None
        self._last_selected_record_quantization = None
        self._rate_selected_color = 'NoteRepeat.RateSelected'
        self._rate_unselected_color = 'NoteRepeat.RateUnselected'
        self._selected_rate_index = DEFAULT_INDEX
        self._on_selected_rate_index_changed.subject = self
        self.__on_selected_track_changed.subject = self.song.view
        self.set_note_repeat(note_repeat)
        self._update_select_buttons()

    @property
    def selected_rate_index(self):
        return self._selected_rate_index

    @selected_rate_index.setter
    def selected_rate(self, new_rate_index):
        assert in_range(new_rate_index, 0, 8) or new_rate_index is None
        self._selected_rate_index = new_rate_index
        self._update_select_buttons()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        self._selected_rate_index = self._get_internal_repeat_rate_index()
        self._on_selected_rate_index_changed(self.selected_rate_index)

    @listens('selected_rate_index')
    def _on_selected_rate_index_changed(self, index):
        self._note_repeat.repeat_rate = NOTE_REPEAT_RATES[index]
        self._selected_rate_index = index
        self.song.view.selected_track.set_data('maschine-note-repeat-rate', NOTE_REPEAT_RATES[index])

    def set_select_buttons(self, buttons):
        self.select_buttons.set_control_element(buttons)

    @select_buttons.pressed
    def _on_select_button_pressed(self, button):
        index = list(self.select_buttons).index(button)
        if in_range(index, 0, 8):
            self._selected_rate_index = index
            self._update_select_buttons()
            self.notify_selected_rate_index(index)

    def _update_select_buttons(self):
        for index, button in enumerate(self.select_buttons):
            if self.is_enabled():
                button.color = self._rate_selected_color if index == self._selected_rate_index else self._rate_unselected_color
            else:
                button.color = 'DefaultButton.Off'

    def set_note_repeat(self, note_repeat):
        note_repeat = note_repeat or DummyNoteRepeat()
        if self._note_repeat is not None:
            self._note_repeat.enabled = False
        self._note_repeat = note_repeat
        self._update_note_repeat(enabled=self.is_enabled())

    def _enable_note_repeat(self):
        self._last_selected_record_quantization = self.song.midi_recording_quantization
        self._set_recording_quantization(False)
        self._update_note_repeat(enabled=True)
        self._update_select_buttons()
        self.select_buttons.enabled = True

    def _disable_note_repeat(self):
        if not self.song.midi_recording_quantization and self._last_selected_record_quantization:
            self._set_recording_quantization(self._last_selected_record_quantization)
        self._update_note_repeat(enabled=False)
        self._update_select_buttons()
        self.select_buttons.enabled = False

    def _set_recording_quantization(self, value):
        def do_it():
            self.song.midi_recording_quantization = value
        self._tasks.parent_task.add(task.run(do_it))

    def _get_internal_repeat_rate(self):
        return self.song.view.selected_track.get_data('maschine-note-repeat-rate', DEFAULT_RATE)

    def _get_internal_repeat_rate_index(self):
        rate = self._get_internal_repeat_rate()
        if rate in NOTE_REPEAT_RATES:
            return NOTE_REPEAT_RATES.index(rate)
        return DEFAULT_INDEX

    def _update_note_repeat(self, enabled):
        self._on_selected_rate_index_changed(self._get_internal_repeat_rate_index())
        self._note_repeat.enabled = enabled

    def update(self):
        super(MaschineNoteRepeat, self).update()
        if self.is_enabled():
            self._enable_note_repeat()
        else:
            self._disable_note_repeat()


class MaschineNoteRepeatEnabler(Component):
    __module__ = __name__
    """
    this is a wrapper for the note repeat component. it gives a button
    to toggle the note repeat component. the wrapper takes care of
    automatically disabling the note repeat component when an audio
    track is selected (including master and return tracks)
    """

    note_repeat_button = ButtonControl(color='DefaultButton.Off')

    def __init__(self, info_display=None, note_repeat=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineNoteRepeatEnabler, self).__init__(*a, **k)
        self.note_repeat_component = MaschineNoteRepeat(note_repeat=note_repeat, name='Note_Repeat', parent=self, is_enabled=False)
        self.__on_selected_track_changed.subject = self.song.view

    @listens('selected_track')
    def __on_selected_track_changed(self):
        self.note_repeat_button.enabled = not self.song.view.selected_track.has_audio_input
        self.note_repeat_component.set_enabled(False)
        self.note_repeat_button.color = 'DefaultButton.Off'

    def set_select_buttons(self, buttons):
        self.note_repeat_component.set_select_buttons(buttons)

    def set_note_repeat_button(self, button):
        self.note_repeat_button.set_control_element(button)

    def set_note_repeat(self, note_repeat):
        self.note_repeat_component.set_note_repeat(note_repeat)

    @note_repeat_button.pressed
    def _on_note_repeat_button_pressed(self, button):
        self._toggle_note_repeat()

    @note_repeat_button.released_delayed
    def _on_note_repeat_button_released_delayed(self, button):
        self._toggle_note_repeat()

    def _toggle_note_repeat(self):
        enabled = self.note_repeat_component.is_enabled()
        self._set_note_repeat_enabled(False if enabled else True)
        self._display_message_on_maschine(enabled)

    def _display_message_on_maschine(self, enabled):
        message = 'Note Repeate is {}'.format('Off' if enabled else 'Active')
        display_task = partial(self._info_display.display_message_on_maschine, message, 3)
        clear_task = partial(self._info_display.clear_display, 3)
        self._tasks.add(task.sequence(task.run(display_task), task.wait(2.5), task.run(clear_task)))

    # ? maybe consider saving and restoring note repeat on track selection ??
    def _restore_note_repeat_enabled_state(self):
        return self._set_note_repeat_enabled(self._get_note_repeat_enabled())

    def _set_note_repeat_enabled(self, is_enabled):
        self.note_repeat_component.set_enabled(is_enabled)
        self.song.view.selected_track.set_data('maschine-note-repeat-rate', is_enabled)
        self.note_repeat_button.color = 'DefaultButton.On' if is_enabled else 'DefaultButton.Off'

    def _get_note_repeat_enabled(self):
        return self.song.view.selected_track.get_data('maschine-note-repeat-rate', False)
