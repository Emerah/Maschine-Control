#
# maschine / ableton
# maschine_control_surface.py
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
from contextlib import contextmanager

from ableton.v2.base import task
from ableton.v2.base.dependency import inject
from ableton.v2.base.util import const
from ableton.v2.control_surface.banking_util import BankingInfo
from ableton.v2.control_surface.components.auto_arm import AutoArmComponent
from ableton.v2.control_surface.control_surface import ControlSurface
from ableton.v2.control_surface.default_bank_definitions import BANK_DEFINITIONS
from ableton.v2.control_surface.device_decorator_factory import DeviceDecoratorFactory
from ableton.v2.control_surface.layer import Layer
from ableton.v2.control_surface.mode import Mode, ModesComponent

from .maschine_device import MaschineDevice
from .maschine_device_navigation import MaschineDeviceNavigation
from .maschine_device_parameter import MaschineDeviceParameter
from .maschine_drums import MaschineDrumRack
from .maschine_elements import MaschineElements
from .maschine_info_display import MaschineInfoDisplay
from .maschine_keyboard import MaschineKeyboard
from .maschine_note_repeat import MaschineNoteRepeatEnabler
from .maschine_playable_modes import MaschinePlayableModes
from .maschine_recording import MaschineRecording
from .maschine_skin import maschine_skin
from .maschine_track_creation import MaschineTrackCreation
from .maschine_track_navigation import MaschineTrackNavigation, MaschineTrackProvider
from .maschine_transport import MaschineTransport

KEYBOARD_CHANNEL = 2
DRUMS_CHANNEL = 1
FEEDBACK_CHANNELS = [KEYBOARD_CHANNEL, DRUMS_CHANNEL]


class MaschineControlSurface(ControlSurface):

    def __init__(self, *a, **k):
        super(MaschineControlSurface, self).__init__(*a, **k)
        self._maschine_injector = inject(element_container=const(None)).everywhere()
        with self.component_guard():
            self._info_display = MaschineInfoDisplay()
            with inject(skin=const(maschine_skin)).everywhere():
                self._elements = MaschineElements()
        self._maschine_injector = inject(element_container=const(self._elements)).everywhere()
        with self.component_guard():
            self.create_auto_arm_component()
            self.create_transport_component()
            self.create_recording_component()
            self.create_track_creation_component()
            self.create_note_repeat_component()
            self.create_keyboard_component()
            self.create_drum_rack_component()
            self.create_device_component()
            self.create_playable_mode()
            self.create_main_modes()
        self.set_feedback_channels(FEEDBACK_CHANNELS)
        self._show_welcome_message()
        self.show_message('Maschine MKiii - ' + str(self.live_version))

    def disconnect(self):
        self._info_display.clear_all_displays()
        self._autoarm.set_enabled(False)
        super(MaschineControlSurface, self).disconnect()

    @contextmanager
    def _component_guard(self):
        with super(MaschineControlSurface, self)._component_guard():
            with self._maschine_injector:
                yield

    @property
    def live_version(self):
        bugfix = self.application.get_bugfix_version()
        minor = self.application.get_minor_version()
        major = self.application.get_major_version()
        current_version = u'Ableton Live {}.{}.{}'.format(major, minor, bugfix)
        return current_version

    def _show_welcome_message(self):
        welcome = 'Welcome to Maschine MKiii'
        live_version = '{}'.format(self.live_version)
        display_welcome = partial(self._info_display.display_message_on_maschine, welcome, 0)
        clear_display = partial(self._info_display.clear_display, 0)
        self._tasks.add(task.sequence(task.run(display_welcome), task.wait(1), task.run(clear_display), task.wait(0.2),
                                      task.run(partial(self._info_display.display_message_on_maschine, self._main_modes.selected_mode.replace('_', ' '), 0))))

        display_live_version = partial(self._info_display.display_message_on_maschine, live_version, 2)
        clear_display = partial(self._info_display.clear_display, 2)
        self._tasks.add(task.sequence(task.run(display_live_version), task.wait(1), task.run(clear_display), task.wait(0.2),
                                      task.run(partial(self._info_display.display_message_on_maschine, 'Track - {}'.format(self.song.view.selected_track.name), 2))))

    def create_auto_arm_component(self):
        self._autoarm = AutoArmComponent(name='AutoArm')

    def create_transport_component(self):
        self._transport = MaschineTransport(name='Transport', is_enabled=False)
        layer = Layer(play_button='play_button', stop_button='stop_button', tap_tempo_button='tap_button', metronome_button='metro_button')
        self._transport.layer = layer
        self._transport.set_enabled(True)

    def create_recording_component(self):
        self._recording = MaschineRecording(name='Recording', is_enabled=False)
        layer = Layer(record_button='record_button', session_automation_button='auto_button')
        self._recording.layer = layer
        self._recording.set_enabled(True)

    def create_track_creation_component(self):
        self._track_creation = MaschineTrackCreation(info_display=self._info_display, name='Track_Creation', is_enabled=False)
        self._track_creation.layer = Layer(return_track_button='return_track_button', audio_track_button='audio_track_button', midi_track_button='midi_track_button')
        self._track_creation.set_enabled(True)

    def create_note_repeat_component(self):
        self._note_repeat = MaschineNoteRepeatEnabler(info_display=self._info_display, note_repeat=self._c_instance.note_repeat, name='Note_Repeat_Enabler', is_enabled=False)
        self._note_repeat.layer = Layer(note_repeat_button='note_repeat_button')
        self._note_repeat.note_repeat_component.layer = Layer(select_buttons='group_matrix')
        self._note_repeat.set_enabled(True)

    def create_drum_rack_component(self):
        self._drum_rack = MaschineDrumRack(translation_channel=DRUMS_CHANNEL, name='Drum_Rack', is_enabled=False)
        self._drum_rack.layer = Layer(matrix='pad_matrix', scroll_page_down_button='chords_button', scroll_page_up_button='step_button')

    def create_keyboard_component(self):
        self._keyboard = MaschineKeyboard(translation_channel=KEYBOARD_CHANNEL, name='Keyboard', is_enabled=False)
        self._keyboard.layer = Layer(matrix='pad_matrix', scroll_down_button='chords_button', scroll_up_button='step_button')

    def create_device_component(self):
        banking_info = BankingInfo(BANK_DEFINITIONS)
        decorator_factory = DeviceDecoratorFactory()
        self._device = MaschineDevice(info_display=self._info_display, device_decorator_factory=decorator_factory, banking_info=banking_info, device_bank_registry=self._device_bank_registry, name='Device', is_enabled=False)
        self._device.layer = Layer(bypass_device_button='console_buttons[4]', previous_bank_button='console_buttons[6]', next_bank_button='console_buttons[7]')  # ,  randomize_button='console_buttons[5]', reset_button='')
        self._device.set_enabled(True)
        self._device_parameter = MaschineDeviceParameter(info_display=self._info_display, parameter_provider=self._device, name='Device_Parameter', is_enabled=False)
        self._device_parameter.layer = Layer(parameter_controls='knob_matrix')
        self._device_parameter.set_enabled(True)
        self._device_navigation = MaschineDeviceNavigation(info_display=self._info_display, device_component=self._device, name='Device_Navigation', is_enabled=False)
        self._device_navigation.layer = Layer(select_buttons='group_matrix', previous_device_button='left_button', next_device_button='right_button', remove_device_button='remove_device_button',
                                              move_backward_button='move_backward_button', move_forward_button='move_forward_button')  # , previous_page_button='pitch_button', next_page_button='mod_button'
        self._device_navigation.set_enabled(True)
        self._track_navigation = MaschineTrackNavigation(info_display=self._info_display, track_provider=MaschineTrackProvider(), name='Track_Navigation', is_enabled=False)
        self._track_navigation.layer = Layer(master_track_button='console_buttons[0]', previous_track_button='console_buttons[1]', next_track_button='console_buttons[2]')
        self._track_navigation.set_enabled(True)

    def create_playable_mode(self):
        self._playable_modes = MaschinePlayableModes(drum_rack=self._drum_rack, keyboard=self._keyboard, name='Playable_Modes', is_enabled=False)
        self._playable_modes.set_enabled(True)

    def create_main_modes(self):
        self._main_modes = ModesComponent(name='Main_Modes')
        self._main_modes.add_mode('device_mode', Mode())
        self._main_modes.add_mode('mixer_mode', Mode())
        self._main_modes.add_mode('browser_mode', Mode())
        self._main_modes.layer = Layer(device_mode_button='plugin_button', mixer_mode_button='mixer_button', browser_mode_button='browser_button')
        self._main_modes.selected_mode = 'device_mode'
