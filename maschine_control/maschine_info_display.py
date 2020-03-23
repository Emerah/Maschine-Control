#
# maschine / ableton
# maschine_info_display.py
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


from ableton.v2.base import depends


class MaschineInfoDisplay(object):
    """
    this object will be automatically injected into all classes subclassed from NIExtendedComponent.
    it has 3 main functions that should concern the end user:
        - display messages on Ableton status bar (Yellow bar)
        - display messages on Maschine MKiii screens
        - clear data displays on Maschine MKiii screens
    """
    @depends(show_message=None, send_midi=None)
    def __init__(self, show_message=None, send_midi=None, *a, **k):
        """Keyword Arguments:
            show_message {function} -- shows messages on Ableton Live's status bar. value will be injected
            by the control surface. (default: {None})

            send_midi {function} -- sends midi messages to Maschine MKiii. value will be injected
            by the control surface. (default: {None})
        """
        assert show_message is not None and callable(show_message)
        assert send_midi is not None and callable(send_midi)
        super(MaschineInfoDisplay, self).__init__(*a, **k)
        self._show_message = show_message
        self._send_midi = send_midi

    def display_message_on_ableton(self, message):
        """displays a message on Live status bar.
        Arguments:
            message {string} -- the message to display on Live status bar
        """
        self._show_message(message)

    def display_message_on_maschine(self, message, screen_index):
        """displays a message on Maschine MKiii screens.
        Arguments:
            message {string} -- message to display on Maschine MKiii screens~
            screen_index {int} -- screen index 0 through 3
        """
        self._send_to_display(message, screen_index)

    def clear_all_displays(self):
        for display_index in range(0, 4):
            self.clear_display(display_index)

    def clear_display(self, display_index):
        self._send_to_display('', display_index)

    def _send_to_display(self, text_message, display_index=0):
        sysex_message = self._make_sysex_message(text_message, display_index)
        self._send_midi(tuple(sysex_message))

    def _make_sysex_message(self, text_message, display_index):
        """creates a proper sysex message
        Arguments:
            text_message {string} -- text message
            display_index {iint} -- which screen to display the message
        Returns:
            tuple -- sysex message ready to be sent to MaschineMKiii screens
        """
        if len(text_message) > 28:
            text_message = text_message[:27]
        sysex_message = [240, 0, 0, 102, 23, 18, min(display_index, 3) * 28]
        filled = text_message.ljust(28)
        for c in filled:
            sysex_message.append(ord(c))
        sysex_message.append(247)
        return sysex_message
