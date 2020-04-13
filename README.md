# Maschine-Control

a set of python scripts built as a useful tool for users of Maschine MK3 and Ableton Live 10.
in a Maschine MK3, every control is accessible and programmable from Ableton python except for
the 2 screens. Until NI gives us access to its HID interface, we are stuck with the ugly mackie
protocol to display information on Maschine MK3 displays. __WHAT A WASTE__

---

## SETUP:

__script folder__: copy 'maschine_control' folder to your 'MIDI Remote Scripts'. make sure Live
is not open or if it were open when you copied the folder, please restart Live.


__ports__: in Live midi settings select the script and set both in and out ports to 
'Maschine Virtual In/Output' (named slightly differently under windows). and activate  
'Track' and 'Remote' for both ports.

__controller editor__: open the 'Maschine-Control' template in the controller editor and use it
with the script


developned and tested under macOS 10.15.x and 10.14.6

---

## Common Controls

__shift button__: 
    
    restart button in the transport section is used for shited operations.  

---

__transport__:  
        
    play, stop, record, tap tempo and toggle metronome [transport section buttons. use shift for metronome]

__recording__:

    record performace and automation [record and automation buttons, long press record button in arrangement 
    view activates recording in overdub mode]

__auto arm__:

    auto arm midi track on selection

__note repeat__:

    note repeat with 8 rates straight and triplets (32t/32/16t/16/8t/8/4t/4) [use note repeat button to 
    enable or disable, and the 8 group buttons to select rate - default to 1/8]

    selected note repeat rate is stored per track, and restored on track selection.

__arranger/session__
    
    switch between arrangement and session views [arranger button]
    
__clip position display__

    maschine mkiii touch strip displays the playing postition of the currently focused detail clip.

    clip position display is disabled while recording.

---

## Pad Matrix Modes

currently the pads offer 2 modes. playable mode and track selection mode. in track selection mode
the pad matrix buttons will select between all the tracks in the session. in playable mode the 
script automatically switches betweem drum rack and instrument modes based on the selected track type 
[audio or midi] and the device type [durm rack or instrument]

    select button: cycles between playable and track selection modes. default is track selection mode.

--- 

__drum rack mode__:

    - scroll drum cell pages up and down [step and chords buttons]
    - play drums racks in full velocity or in velocity sensetive mode. [fixed vel button]
    - solo and mute drum pads with color indication of drum pad state [solo and mute buttons]
    - when a drum rack has more than 16 pads to play, each cell page colors the pads differently.

    - playable simpler chopped loopes (NotImplementedYet)

__instrument mode__:

    - select a scales for instrument tracks [pad mode and keyboard buttons]
    - select a key for instrument tracks [shift + pad mode and keyboard buttons]
    - scroll keyboard octaves up and down [step and chords buttons]
    - pad colors shows scale notes and non-scale note in different colors

__track selection mode__

    - enable/disable selection matrix [select button]
    - select tracks via the pad matrix [pad matrix]
    - scroll pages of 16 tracks [chords and step button]
    - return tracks and master tracks are colored differenly for visual distinction
    - selection button is momentrary facilitate faster work flow.

---

## Main Modes

#### Device Control Mode


device control

    - control selected device's parameters [console knobs]
    - bypass/activate selected device. [console buttons: 5]
    - remove the selected device from the device chain. [shift + console button: 5]
    - reset selected device to default state. [console button: 6]
    - randomize selected device's parameters values. [shift + console button: 6]

selection:

    - select devices from a device chain. [encoder buttons: left and right]
    - select parameter banks of the selected device. [console buttons: 7 and 8]
    - select pages of devices when more than 8 devices are present on the selected track. 
      [shift + 4-D encoder left and right buttons]
    - select rack chains if the selected device is a rack with chains [4-D encoder up and down]
    - select master track or previous and next track in the live set. [console buttons: 1, 2, 3]

organize devices

    - move devices backward and forward in the device chain. [shift + console buttons 7 + 8]
    - show/hide chain devices if the selected device is an instrument or drum rack [4-D encoder click]
    - collapse/show selected device [4-D encoder click]

create tracks

    - create new audio, return, and midi tracks [shift + console buttons: 1, 2, 3]

---

#### Mixer Control Mode:
    
    - NotImplementedYet

---

#### Browser Control Mode:

    - NotImplementedYet

---

#### Information Display:

    - welcome and current live version message
    - current mode name
      
    in device mode users will always see the following information on Maschine MK3 screens:
        - mode name
        - selected track name
        - selected device name
        - selected parameter bank name
        - selected parameter name and value
        - device active state notification
        - note repeate active state notification
        - note repeat selected rate notification (NotImplementedYet)
        - new track notification
        - current view notification
        - selected key and scale notification
        - warning message when trying to create more than 12 sends

    information updates on changes in track, device, bank, and parameter selection, or change in parameters value. 
    message display operations are tasked to the components and to the controller surface to enable timed and
    automated messages.

---

#### Important Notes about the controller editor template

the controls in the attached controller editor template uses channel 16 to send and channels 2, 3 for
feedback.

all used controls "led on" section is set to "on midi in". this is necessary for midi feedback from Live
to Maschine MK3 controls. if a control is set to "on midi out" the control light will always respond to
presses instead of listening to Live for feedback.

the pads and group buttons and (secretly the sampling button) can multi colors. the "color mode" is set
to indexed so that these buttons can listen to the scripts and display correct skinning colors incoming
from Live.

please keep that info in mind if you try to customize/relocate controls.