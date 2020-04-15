#
# native instruments / ableton
# maschine_device.py
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
from ableton.v2.base.event import listens
from ableton.v2.control_surface.components.device import DeviceComponent
from ableton.v2.control_surface.parameter_provider import ParameterInfo
from ableton.v2.base.util import clamp, in_range
from ableton.v2.control_surface.control.button import ButtonControl
from ableton.v2.base import task
from functools import partial
import random


class MaschineDevice(DeviceComponent):

    __events__ = (u'bank',)

    previous_bank_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.Off')
    next_bank_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.Off')
    bypass_device_button = ButtonControl(color='DefaultButton.Off')
    reset_parameters_button = ButtonControl(color='DefaultButton.Off')
    randomize_parameters_button = ButtonControl(color='DefaultButton.Off')

    @depends(info_display=None)
    def __init__(self, info_display=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        self._quantized_parameters = {}
        super(MaschineDevice, self).__init__(*a, **k)
        self.__on_bank_changed.subject = self._device_bank_registry
        self.update_bank_buttons()

    @property
    def device_is_active(self):
        return self.device() and self.device().parameters[0].value != 0

    @listens('is_active')
    def __on_is_active_changed(self):
        self.update_bypass_button()
        if self.device():
            message = '{} - {}'.format('Activated' if self.device_is_active else 'Bypassed', self.device().name)
            self._display_temprary_message_on_maschine(message, 1)

    @listens('device_bank')
    def __on_bank_changed(self, device, bank):
        if device == self.device():
            self._set_bank_index(bank)
            self.update_bank_buttons()
            self.notify_bank()
            self._display_message_on_maschine()

    def set_previous_bank_button(self, button):
        self.previous_bank_button.set_control_element(button)

    def set_next_bank_button(self, button):
        self.next_bank_button.set_control_element(button)

    def set_bypass_device_button(self, button):
        self.bypass_device_button.set_control_element(button)

    def set_reset_parameters_button(self, button):
        self.reset_parameters_button.set_control_element(button)

    def set_randomize_parameters_button(self, button):
        self.randomize_parameters_button.set_control_element(button)

    @previous_bank_button.pressed
    def _on_previous_bank_button_pressed(self, button):
        self.select_previous_bank()

    @next_bank_button.pressed
    def _on_next_bank_button_pressed(self, button):
        self.select_next_bank()

    @bypass_device_button.pressed
    def _on_bypass_device_button_pressed(self, button):
        self.toggle_device_active_state()
        self.update_bypass_button()

    @reset_parameters_button.pressed
    def _on_reset_parameters_button_pressed(self, button):
        self.reset_device_parameters()

    @randomize_parameters_button.pressed
    def _on_randomize_parameters_button_pressed(self, button):
        self.randomize_device_parameters()

    def select_previous_bank(self):
        self._scroll_banks(-1)

    def select_next_bank(self):
        self._scroll_banks(1)

    def toggle_device_active_state(self):
        if self.device():
            parameter = self.device().parameters[0]
            if parameter.is_enabled:
                self.device().parameters[0].value = False if self.device_is_active else True

    def reset_device_parameters(self):
        if self.device() is None:
            return
        parameters = filter(lambda param: param.is_enabled and param.state == 0, self.device().parameters)
        for i in range(0, len(parameters)):
            p = parameters[i]
            if not p.is_quantized:
                p.value = p.default_value
            else:
                if p.name in self._quantized_parameters:
                    p.value = self._quantized_parameters[p.name]
        # self._display_temprary_message_on_maschine('Device Reset to defaults', 3)

    def randomize_device_parameters(self):
        if self.device() is None:
            return
        parameters = filter(lambda param:  param.is_enabled and param.state == 0, self.device().parameters[1:])
        for p in parameters:
            if not p.is_quantized:
                value = random.random()
                scaled_value = p.min + (value * (p.max - p.min))
                if in_range(scaled_value, p.min, p.max):
                    p.value = scaled_value

    def _scroll_banks(self, offset):
        if self._bank:
            bank_index = clamp(self._bank.index + offset, 0, self._bank.bank_count())
            self._device_bank_registry.set_device_bank(self.device(), bank_index)
            self._set_bank_index(bank_index)

    def update_bypass_button(self):
        self.bypass_device_button.enabled = self.device() is not None
        self.bypass_device_button.color = 'DefaultButton.Off' if self.device_is_active else 'DefaultButton.On'

    def update_bank_buttons(self):
        self.previous_bank_button.enabled = self._bank is not None and self._bank.index > 0
        self.next_bank_button.enabled = self._bank is not None and self._bank.index + 1 < self._bank.bank_count()

    def _set_device(self, device):
        super(MaschineDevice, self)._set_device(device)
        self.__on_is_active_changed.subject = device
        self.update_bank_buttons()
        self.update_bypass_button()
        if device:
            self._collect_device_quantized_parameters(device)
            self._display_message_on_maschine()

    def _collect_device_quantized_parameters(self, device):
        if not device.can_have_chains:
            parameters = device.parameters
            for parameter in parameters:
                if parameter.is_enabled and parameter.is_quantized:
                    self._quantized_parameters[parameter.name] = parameter.value

    def _create_parameter_info(self, parameter, name):
        parameter_info = ParameterInfo(parameter=parameter, name=name, default_encoder_sensitivity=1.0, fine_grain_encoder_sensitivity=0.1)
        return parameter_info

    def _display_temprary_message_on_maschine(self, message, display_index):
        self._tasks.clear()
        self._info_display.clear_display(display_index)
        temp_display = partial(self._info_display.display_message_on_maschine, message, display_index)
        clear_display = partial(self._info_display.clear_display, display_index)
        self._tasks.add(task.sequence(task.run(temp_display), task.wait(2.5), task.run(clear_display), task.run(self._display_message_on_maschine)))

    def _display_message_on_maschine(self):
        if self.device():
            self._info_display.clear_display(1)
            message = '{} - {}'.format(self.device().name or '', self._bank.name or '')
            self._info_display.display_message_on_maschine(message, 1)
