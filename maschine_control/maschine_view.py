#
# maschine / ableton
# maschine_view.py
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
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control.button import ButtonControl

VIEWS = (u'Browser', u'Arranger', u'Session', u'Detail', u'Detail/Clip', u'Detail/DeviceChain')


class MaschineView(Component):

    view_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    def __init__(self, info_display=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineView, self).__init__(*a, **k)

    @view_button.pressed
    def _on_view_toggled(self, button):
        self.toggle_main_view()

    def toggle_main_view(self):
        view = ''
        app_view = self.application.view
        if app_view.is_view_visible('Session'):
            self.show_view('Arranger')
            view = 'arranger'
        else:
            self.show_view('Session')
            view = 'session'
        self._display_message_on_maschine(view)

    def show_view(self, view):
        assert view in VIEWS
        app_view = self.application.view
        try:
            if view == 'Detail/DeviceChain' or 'Detail/Clip':
                if not app_view.is_view_visible('Detail'):
                    app_view.show_view('Detail')
            if not app_view.is_view_visible(view):
                app_view.show_view(view)
        except RuntimeError:
            pass

    def _display_message_on_maschine(self, view):
        message = 'In {} View'.format(view)
        display_task = partial(self._info_display.display_message_on_maschine, message, 3)
        clear_task = partial(self._info_display.clear_display, 3)
        self._tasks.add(task.sequence(task.run(display_task), task.wait(1), task.run(clear_task)))
