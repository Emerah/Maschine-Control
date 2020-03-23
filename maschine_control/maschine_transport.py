#
# maschine / ableton
# maschine_transport.py
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


from ableton.v2.control_surface.components.transport import TransportComponent
from ableton.v2.control_surface.control.button import ButtonControl


class MaschineTransport(TransportComponent):
    """
    this override changes the following from the default behavious:
        - reverses the stop button color behaviour
        - reverses tap_tempo_button lighting behaviour
    """
    # ? consider adding follow_song + observer

    tap_tempo_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    def __init__(self, *a, **k):
        super(MaschineTransport, self).__init__(*a, **k)

    def _update_stop_button_color(self):
        self.stop_button.color = 'DefaultButton.Off' if self.song.is_playing else 'DefaultButton.On'

    @tap_tempo_button.pressed
    def tap_tempo_button(self, _):
        if not self._end_undo_step_task.is_running:
            self.song.begin_undo_step()
        self._end_undo_step_task.restart()
        self.song.tap_tempo()

    def set_tap_tempo_button(self, button):
        self.tap_tempo_button.set_control_element(button)
