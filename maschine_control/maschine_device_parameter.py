#
# native instruments / ableton
# maschine_device_parameter.py
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

from ableton.v2.base.dependency import depends
from ableton.v2.base.event import listens, listens_group
from ableton.v2.control_surface.components import DisplayingDeviceParameterComponent


class MaschineDeviceParameter(DisplayingDeviceParameterComponent):

    # todo: this should eventually display parameter names when knobs get touched in device mode

    @depends(info_display=None)
    def __init__(self, info_display=None, parameter_provider=None,  *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineDeviceParameter, self).__init__(parameter_provider=parameter_provider, *a, **k)
        self.__on_selected_parameter_changed.subject = self.song.view

    @listens_group('value')
    def _on_parameter_value_changed(self, parameter):
        self._update_parameter_values()
        self.display_parameter_info(parameter)

    def display_parameter_info(self, parameter):
        message = self._create_formatted_message(parameter)
        self._info_display.display_message_on_maschine(message, 3)
        self._info_display.display_message_on_ableton(message)

    def _create_formatted_message(self, parameter):
        value = parameter.value
        formatted_value = parameter.str_for_value(value) if hasattr(parameter, 'str_for_value') else (value/parameter.max*100)
        message = '{}: {}'.format(parameter.name, formatted_value)
        return message

    @listens('selected_parameter')
    def __on_selected_parameter_changed(self):
        parameter = self.song.view.selected_parameter
        if parameter is not None:
            self._info_display.display_message_on_ableton('{}'.format(parameter.name))
            self._info_display.display_message_on_maschine('{}'.format(parameter.name), 3)
        else:
            self._info_display.clear_display(3)
