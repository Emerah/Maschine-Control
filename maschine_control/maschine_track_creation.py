#
# native instruments / ableton
# maschine_track_creation.py
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

from functools import partial
from ableton.v2.base.dependency import depends
from ableton.v2.base import task
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control.button import ButtonControl


class MaschineTrackCreation(Component):
    midi_track_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    audio_track_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    return_track_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    @depends(info_display=None)
    def __init__(self, info_display=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineTrackCreation, self).__init__(*a, **k)

    @property
    def selected_track(self):
        return self.song.view.selected_track

    @property
    def master_track(self):
        return self.song.master_track

    @property
    def return_tracks(self):
        return self.song.return_tracks

    @midi_track_button.pressed
    def _on_midi_track_button_pressed(self, _):
        self._create_new_midi_track()

    @audio_track_button.pressed
    def _on_audio_track_button_pressed(self, _):
        self._create_new_audio_track()

    @return_track_button.pressed
    def _on_return_track_button_pressed(self, _):
        self._create_new_return_track()

    def _create_new_midi_track(self):
        track = self.selected_track
        master = self.master_track
        if track == master or track in list(self.return_tracks):
            self.song.create_midi_track(-1)
        else:
            self.song.create_midi_track()
        self._display_message_on_maschine('midi')

    def _create_new_audio_track(self):
        track = self.selected_track
        master = self.master_track
        if track == master or track in list(self.return_tracks):
            self.song.create_audio_track(-1)
        else:
            self.song.create_audio_track()
        self._display_message_on_maschine('audio')

    def _create_new_return_track(self):
        if len(self.song.return_tracks) < 12:
            self.song.create_return_track()
            self._display_message_on_maschine('return')
        else:
            self._info_display.clear_display(3)
            self._tasks.clear()
            message = 'Only 12 sends allowed'
            display_task = partial(self._info_display.display_message_on_maschine, message, 3)
            clear_display = partial(self._info_display.clear_display, 3)
            self._tasks.add(task.sequence(task.run(display_task), task.wait(1), task.run(clear_display)))

    def _display_message_on_maschine(self, track_type):
        self._tasks.clear()
        self._info_display.clear_display(3)
        message = 'Created New {} Track'.format(track_type)
        display_task = partial(self._info_display.display_message_on_maschine, message, 3)
        clear_display = partial(self._info_display.clear_display, 3)
        self._tasks.add(task.sequence(task.run(display_task), task.wait(1), task.run(clear_display)))
