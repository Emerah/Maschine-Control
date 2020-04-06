#
# maschine / ableton
# maschine_skin.py
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

from ableton.v2.control_surface.elements.color import Color
from ableton.v2.control_surface.skin import Skin


class MaschineIndexedColor:
    """
    this list of colors represents the maschine colors in indexed mode according to the controller editor manual.
    this is why in the controller editor template, colored buttons (pads and group buttons) leds must be set to
    light on "midi in" and color to "indexed" mode.
    """
    BLACKDim = Color(0)
    BLACKDimFlash = Color(1)
    BLACK = Color(2)
    BLACKBrightFlash = Color(3)
    REDDim = Color(4)
    REDDimFlash = Color(5)
    RED = Color(6)
    REDBrightFlash = Color(7)
    ORANGEDim = Color(8)
    ORANGEDimFlash = Color(9)
    ORANGE = Color(10)
    ORANGEBrightFlash = Color(11)
    LIGHTORANGEDim = Color(12)
    LIGHTORANGEDimFlash = Color(13)
    LIGHTORANGE = Color(14)
    LIGHTORANGEBrightFlash = Color(15)
    WARMYELLOWDim = Color(16)
    WARMYELLOWDimFlash = Color(17)
    WARMYELLOW = Color(18)
    WARMYELLOWBrightFlash = Color(19)
    YELLOWDim = Color(20)
    YELLOWDimFlash = Color(21)
    YELLOW = Color(22)
    YELLOWBrightFlash = Color(23)
    LIMEDim = Color(24)
    LIMEDimFlash = Color(25)
    LIME = Color(26)
    LIMEBrightFlash = Color(27)
    GREENDim = Color(28)
    GREENDimFlash = Color(29)
    GREEN = Color(30)
    GREENBrightFlash = Color(31)
    MINTDim = Color(32)
    MINTDimFlash = Color(33)
    MINT = Color(34)
    MINTBrightFlash = Color(35)
    CYANDim = Color(36)
    CYANDimFlash = Color(37)
    CYAN = Color(38)
    CYANBrightFlash = Color(39)
    TURQUOISEDim = Color(40)
    TURQUOISEDimFlash = Color(41)
    TURQUOISE = Color(42)
    TURQUOISEBrightFlash = Color(43)
    BLUEDim = Color(44)
    BLUEDimFlash = Color(45)
    BLUE = Color(46)
    BLUEBrightFlash = Color(47)
    PLUMDim = Color(48)
    PLUMDimFlash = Color(49)
    PLUM = Color(50)
    PLUMBrightFlash = Color(51)
    VIOLETDim = Color(52)
    VIOLETDimFlash = Color(53)
    VIOLET = Color(54)
    VIOLETBrightFlash = Color(55)
    PURPLEDim = Color(56)
    PURPLEDimFlash = Color(57)
    PURPLE = Color(58)
    PURPLEBrightFlash = Color(59)
    MAGENTADim = Color(60)
    MAGENTADimFlash = Color(61)
    MAGENTA = Color(62)
    MAGENTABrightFlash = Color(63)
    FUCHSIADim = Color(64)
    FUCHSIADimFlash = Color(65)
    FUCHSIA = Color(66)
    FUCHSIABrightFlash = Color(67)
    WHITEDim = Color(68)
    WHITEDimFlash = Color(69)
    WHITE = Color(70)
    WHITEBrightFlash = Color(71)


ON = Color(127)
OFF = Color(0)


class Colors:

    class DefaultButton:
        On = ON
        Off = OFF
        Disabled = OFF

    class Transport:
        PlayOn = ON
        PlayOff = OFF

    class Mixer:
        pass

    class Mode:

        class DeviceMode:
            On = ON
            Off = OFF

        class MixerMode:
            On = ON
            Off = OFF

        class BrowserMode:
            On = ON
            Off = OFF

        class PlayableMode:
            On = ON
            Off = OFF

        class TrackSelectionMode:
            On = ON
            Off = OFF

    class Accent:
        On = ON
        Off = OFF

    class ItemNavigation:
        NoItem = MaschineIndexedColor.BLACK
        ItemSelected = MaschineIndexedColor.LIME
        ItemNotSelected = MaschineIndexedColor.LIMEDim
        RackItemSelected = MaschineIndexedColor.PLUM
        RackItemNotSelected = MaschineIndexedColor.PLUMDim

    class TrackNavigation:
        NoTrack = MaschineIndexedColor.BLACK
        TrackSelected = MaschineIndexedColor.ORANGE
        TrackNotSelected = MaschineIndexedColor.ORANGEDim
        ReturnTrackSelected = MaschineIndexedColor.WARMYELLOW
        ReturnTrackNotSelected = MaschineIndexedColor.WARMYELLOWDim
        MasterTrackSelected = MaschineIndexedColor.LIME
        MasterTrackNotSelected = MaschineIndexedColor.LIMEDim

    class NoteRepeat:
        RateSelected = MaschineIndexedColor.MINT
        RateUnselected = MaschineIndexedColor.MINTDim

    class Keyboard:
        NotePressed = MaschineIndexedColor.WARMYELLOW
        Natural = MaschineIndexedColor.YELLOWDim
        Sharp = MaschineIndexedColor.BLUEDim

    class DrumGroup:
        NotePressed = MaschineIndexedColor.WARMYELLOW
        PadEmpty = MaschineIndexedColor.BLACK
        PadFilled = MaschineIndexedColor.YELLOWDim
        PadSelected = MaschineIndexedColor.YELLOW
        PadMuted = MaschineIndexedColor.ORANGEDim
        PadMutedSelected = MaschineIndexedColor.ORANGE
        PadSoloed = MaschineIndexedColor.BLUEDim
        PadSelectedNotSoloed = MaschineIndexedColor.YELLOW
        PadSoloedSelected = MaschineIndexedColor.BLUE
        PadQuadrant0 = MaschineIndexedColor.BLUEDim
        PadQuadrant1 = MaschineIndexedColor.GREENDim
        PadQuadrant2 = MaschineIndexedColor.YELLOWDim
        PadQuadrant3 = MaschineIndexedColor.PURPLEDim
        PadQuadrant4 = MaschineIndexedColor.ORANGEDim
        PadQuadrant5 = MaschineIndexedColor.CYANDim
        PadQuadrant6 = MaschineIndexedColor.PLUMDim
        PadQuadrant7 = MaschineIndexedColor.WARMYELLOWDim


"""
eventually after  mixer component iscompleted, this should be called
from the main control surface for song injection, which is a dependency
for using dynamic colors for tracks and clips.
"""
maschine_skin = Skin(Colors)
