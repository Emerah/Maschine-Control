#
# maschine / ableton
# maschine_recording.py
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


from ableton.v2.base import listens
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.component import Component


class MaschineRecording(Component):
    """simple record transport section
    record: will toggle session record in session view, arrangement record in arranger.
    a long press on record button in arrangement view, will trigger recording in overdub mode.
    """

    record_button = ButtonControl(color=u'DefaultButton.Off')
    session_automation_button = ButtonControl(color=u'DefaultButton.Off')

    def __init__(self, *a, **k):
        super(MaschineRecording, self).__init__(*a, **k)
        self.setup_observers()

    def setup_observers(self):
        song = self.song
        app_view = self.application.view
        self.__on_record_mode_changed.subject = song
        self.__on_session_record_chanaged.subject = song
        self.__on_session_automation_record_changed.subject = song
        self.__on_main_view_changed.subject = app_view
        self.__on_record_mode_changed()
        self.__on_session_record_chanaged()
        self.__on_session_automation_record_changed()
        self.__on_main_view_changed()

    @property
    def is_recording(self):
        if self.current_view == u'Session':
            return self.song.session_record
        else:
            return self.song.record_mode

    @property
    def current_view(self):
        session = self.application.view.is_view_visible(u'Session')
        return u'Session' if session else u'Arranger'

    @listens(u'record_mode')
    def __on_record_mode_changed(self):
        self._update_record_button_color()

    def _update_record_button_color(self):
        self.record_button.color = u'DefaultButton.On' if self.is_recording else u'DefaultButton.Off'

    @listens(u'session_record')
    def __on_session_record_chanaged(self):
        self._update_record_button_color()

    @listens(u'session_automation_record')
    def __on_session_automation_record_changed(self):
        self.session_automation_button.color = u'DefaultButton.On' if self.song.session_automation_record else u'DefaultButton.Off'

    @listens(u'is_view_visible', u'Session')
    def __on_main_view_changed(self):
        self._update_record_button_color()

    def _update_record_button_colors(self):
        if self.current_view == u'Session':
            self.__on_session_record_chanaged()
        else:
            self.__on_record_mode_changed()

    @record_button.pressed
    def _on_record_button_pressed(self, _):
        self.handle_recording()

    @record_button.pressed_delayed
    def _on_record_button_pressed_delayed(self, _):
        self.toggle_arrangement_overdub()

    @session_automation_button.pressed
    def _on_session_automation_button_pressed(self, _):
        self.toggle_session_automation()

    def handle_recording(self):
        if self.current_view == u'Session':
            self.toggle_session_record()
        else:
            self.toggle_arrangement_record()

    def toggle_arrangement_record(self):
        self.song.record_mode = False if self.is_recording else True
        if self.song.arrangement_overdub:
            self.song.arrangement_overdub = False

    def toggle_arrangement_overdub(self):
        if self.current_view == u'Arranger':
            self.song.arrangement_overdub = not self.song.arrangement_overdub

    def toggle_session_record(self):
        self.song.session_record = False if self.is_recording else True

    def toggle_session_automation(self):
        self.song.session_automation_record = False if self.song.session_automation_record else True
