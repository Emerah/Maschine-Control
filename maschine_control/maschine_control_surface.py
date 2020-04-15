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

from contextlib import contextmanager
from functools import partial

from ableton.v2.base import task
from ableton.v2.base.dependency import inject
from ableton.v2.base.util import const
from ableton.v2.control_surface.banking_util import BankingInfo
from ableton.v2.control_surface.components.auto_arm import AutoArmComponent
from ableton.v2.control_surface.control_surface import ControlSurface
from ableton.v2.control_surface.default_bank_definitions import BANK_DEFINITIONS
from ableton.v2.control_surface.device_decorator_factory import DeviceDecoratorFactory
from ableton.v2.control_surface.elements.full_velocity_element import FullVelocityElement
from ableton.v2.control_surface.layer import Layer
from ableton.v2.control_surface.mode import LayerMode, Mode, ModesComponent

from .maschine_clip_position import MaschineClipPositionIndicator
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
from .maschine_track_navigation import MaschineTrackNavigator
from .maschine_track_selection import MaschineTrackProvider
from .maschine_track_selection import MaschineTrackSelection
from .maschine_transport import MaschineTransport
from .maschine_view import MaschineView
from .maschine_welcome import MaschineWelcome

KEYBOARD_CHANNEL = 2
DRUMS_CHANNEL = 1
FEEDBACK_CHANNELS = [KEYBOARD_CHANNEL, DRUMS_CHANNEL]


class MaschineControlSurface(ControlSurface):

    def __init__(self, *a, **k):
        super(MaschineControlSurface, self).__init__(*a, **k)
        self._maschine_injector = inject(element_container=const(None), info_display=const(None)).everywhere()
        with self.component_guard():
            self._info_display = MaschineInfoDisplay()
            with inject(skin=const(maschine_skin)).everywhere():
                self._elements = MaschineElements()
        self._maschine_injector = inject(element_container=const(self._elements), info_display=const(self._info_display)).everywhere()
        with self.component_guard():
            self.create_auto_arm_component()
            self.create_view_switcher_component()
            self.create_clip_position_indicator_component()
            self.create_transport_component()
            self.create_recording_component()
            self.create_track_creation_component()
            self.create_note_repeat_component()
            self.create_drum_rack_component()
            self.create_keyboard_component()
            self.create_track_selection_matrix_component()
            self.create_playable_mode()
            self.create_pad_matrix_modes()
            self.create_device_component()
            self.create_main_modes()
            self.create_welcome_component()
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

    def create_welcome_component(self):
        self._welcome = MaschineWelcome(name='Welcome')
        self._welcome.layer = Layer(pads='pad_matrix', group_buttons='group_matrix')
        self._tasks.add(task.sequence(task.wait(2), task.run(partial(self._welcome.set_enabled, False))))

    def create_view_switcher_component(self):
        self._view_switcher = MaschineView(name='View_Switcher', is_enabled=False)
        self._view_switcher.layer = Layer(view_button='arranger_button')
        self._view_switcher.set_enabled(True)

    def create_clip_position_indicator_component(self):
        self._clip_position = MaschineClipPositionIndicator(name='Clip_Position', is_enabled=False)
        self._clip_position.layer = Layer(touch_strip_display='touch_strip')
        self._clip_position.set_enabled(True)

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
        self._track_creation = MaschineTrackCreation(name='Track_Creation', is_enabled=False)
        self._track_creation.layer = Layer(return_track_button='return_track_button', audio_track_button='audio_track_button', midi_track_button='midi_track_button')
        self._track_creation.set_enabled(True)

    def create_note_repeat_component(self):
        self._note_repeat = MaschineNoteRepeatEnabler(note_repeat=self._c_instance.note_repeat, name='Note_Repeat_Enabler', is_enabled=False)
        self._note_repeat.layer = Layer(note_repeat_button='note_repeat_button')
        self._note_repeat.note_repeat_component.layer = Layer(select_buttons='group_matrix')
        self._note_repeat.set_enabled(True)

    def create_drum_rack_component(self):
        self._drum_rack = MaschineDrumRack(translation_channel=DRUMS_CHANNEL, name='Drum_Rack', is_enabled=False)
        full_velocity_element = FullVelocityElement(full_velocity=self._c_instance.full_velocity)
        self._drum_rack.layer = Layer(matrix='pad_matrix', scroll_page_down_button='chords_button', scroll_page_up_button='step_button',
                                      mute_button='mute_button', solo_button='solo_button', accent_button='fixed_vel_button', full_velocity=full_velocity_element)

    def create_keyboard_component(self):
        self._keyboard = MaschineKeyboard(translation_channel=KEYBOARD_CHANNEL, name='Keyboard', is_enabled=False)
        self._keyboard.layer = Layer(matrix='pad_matrix', scroll_down_button='chords_button', scroll_up_button='step_button', next_scale_button='keyboard_button',
                                     previous_scale_button='pad_mode_button', next_key_button='next_key_button', previous_key_button='previous_key_button')

    def create_track_selection_matrix_component(self):
        self._track_selection_matrix = MaschineTrackSelection(track_provider=MaschineTrackProvider(), name='Track_Selection_Matrix', is_enabled=False)
        self._track_selection_matrix.layer = Layer(select_buttons='selection_matrix', previous_track_page_button='chords_button', next_track_page_button='step_button')

    def create_playable_mode(self):
        self._playable_mode = MaschinePlayableModes(drum_rack=self._drum_rack, keyboard=self._keyboard, name='Playable_Modes', is_enabled=False)

    def create_pad_matrix_modes(self):
        self._pad_modes = ModesComponent('Pad_Modes')
        self._pad_modes.layer = Layer(cycle_mode_button='select_button')
        self._pad_modes.add_mode('playable_mode', self._playable_mode)
        self._pad_modes.add_mode('track_selection_mode', self._track_selection_matrix)
        self._pad_modes.selected_mode = 'track_selection_mode'

    def create_device_component(self):
        banking_info = BankingInfo(BANK_DEFINITIONS)
        decorator_factory = DeviceDecoratorFactory()
        self._device = MaschineDevice(device_decorator_factory=decorator_factory, banking_info=banking_info, device_bank_registry=self._device_bank_registry, name='Device')
        self._device_parameter = MaschineDeviceParameter(parameter_provider=self._device, name='Device_Parameter')
        self._device_navigation = MaschineDeviceNavigation(device_component=self._device, name='Device_Navigation')
        self._track_navigation = MaschineTrackNavigator(name='Track_Navigator')

    def create_main_modes(self):
        self._main_modes = ModesComponent(name='Main_Modes')
        layer = Layer(bypass_device_button='console_buttons[4]', reset_parameters_button='console_buttons[5]', previous_bank_button='console_buttons[6]',
                      next_bank_button='console_buttons[7]', randomize_parameters_button='randomize_parameters_button')
        device_mode = LayerMode(self._device, layer=layer)
        layer = Layer(parameter_controls='knob_matrix')
        device_parameter_mode = LayerMode(self._device_parameter, layer=layer)
        layer = Layer(select_buttons='group_matrix', previous_device_button='left_button', next_device_button='right_button', remove_device_button='remove_device_button',
                      move_backward_button='move_backward_button', move_forward_button='move_forward_button', collapse_device_button='click_button',
                      next_chain_button='down_button', previous_chain_button='up_button', next_page_button='next_device_page_button', previous_page_button='previous_device_page_button')
        device_navigation_mode = LayerMode(self._device_navigation, layer=layer)
        layer = Layer(master_track_button='console_buttons[0]', previous_track_button='console_buttons[1]', next_track_button='console_buttons[2]')
        track_navigation_mode = LayerMode(self._track_navigation, layer=layer)
        self._main_modes.add_mode('device_contol_mode', [device_mode, device_parameter_mode, device_navigation_mode, track_navigation_mode])
        self._main_modes.add_mode('mixer_contol_mode', Mode())
        self._main_modes.add_mode('browser_contol_mode', Mode())
        self._main_modes.layer = Layer(device_contol_mode_button='plugin_button', mixer_contol_mode_button='mixer_button', browser_contol_mode_button='browser_button')
        self._main_modes.selected_mode = 'device_contol_mode'
