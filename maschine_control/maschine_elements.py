#
# maschine / ableton
# maschine_elements.py
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

import Live  # noqa

from ableton.v2.base.dependency import depends
from ableton.v2.control_surface.elements.button import ButtonElement
from ableton.v2.control_surface.elements.button_matrix import ButtonMatrixElement
from ableton.v2.control_surface.elements.combo import ComboElement
from ableton.v2.control_surface.elements.encoder import EncoderElement
from ableton.v2.control_surface.elements.slider import SliderElement
from ableton.v2.control_surface.input_control_element import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from ableton.v2.control_surface.resource import PrioritizedResource

DEFAULT_CHANNEL = 15
RELATIVE_SMOOTH = None


@depends(skin=None)
def create_button(name, identifier, skin=None, **k):
    button = ButtonElement(is_momentary=True, msg_type=MIDI_CC_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, skin=skin, name=name, **k)
    return button


@depends(skin=None)
def create_pad(name, identifier, skin=None, **k):
    button = ButtonElement(is_momentary=True, msg_type=MIDI_NOTE_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, skin=skin, name=name, **k)
    return button


def create_encoder(name, identifier, **k):
    encoder = EncoderElement(msg_type=MIDI_CC_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, map_mode=RELATIVE_SMOOTH, encoder_sensitivity=1.0, name=name, **k)
    encoder.set_feedback_delay(-1)
    encoder.mapping_sensitivity = 0.2
    return encoder


def create_knob(name, identifier, **k):
    knob = SliderElement(msg_type=MIDI_CC_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, name=name, **k)
    knob.set_feedback_delay(-1)
    knob.mapping_sensitivity = 0.2
    return knob


def create_matrix(name, controls, **k):
    rows = controls if isinstance(controls[0], list) else [controls]
    matrix = ButtonMatrixElement(rows=rows, name=name)
    return matrix


class MaschineElements(object):

    def __init__(self, *a, **k):
        super(MaschineElements, self).__init__(*a, **k)

        # shift button
        self.restart_button = create_button('Restart', 53, resource_type=PrioritizedResource)

        def with_shift(name, control):
            return ComboElement(control=control, modifier=self.restart_button, name=name)

        # mode buttons
        self.plugin_button = create_button('Plugin', 35)
        self.mixer_button = create_button('Mixer', 37)
        self.browser_button = create_button('Browser', 38)

        # transport buttons
        self.play_button = create_button('Play', 57)
        self.stop_button = create_button('Stop', 59)
        self.tap_button = create_button('Tap', 55)
        self.metro_button = with_shift('Metro', self.tap_button)

        # recording buttons
        self.record_button = create_button('Record', 58)
        self.auto_button = create_button('Auto', 42)
        self.re_enable_auto_button = with_shift('Re_Enable_Auto', self.auto_button)

        # note repeat
        self.note_repeat_button = create_button('Note_Repeat', 46)

        self.group_buttons = [create_button('Group_{}'.format(index), index + 100) for index in xrange(8)]
        self.group_matrix = create_matrix('Group_Matrix', self.group_buttons)

        # drum rack matrix
        self.drum_cells = [[create_pad(('{}_Pad_{}').format(col_index, row_index), offset + col_index) for col_index in xrange(4)] for row_index, offset in enumerate(xrange(48, 32, -4))]
        self.drum_rack_matrix = create_matrix('Drum_Rack_Matrix', self.drum_cells)
        self.chords_button = create_button('Chords', 83)
        self.step_button = create_button('Step', 84)
