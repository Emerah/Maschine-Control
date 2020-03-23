# Maschine-Control

a set of python scripts built as a useful tool for users of Maschine MK3 and Ableton Live 10. 
n a Maschine MK3, every control is accessible and programmable from Ableton python except for 
the 2 screens. Until NI gives us access to its HID interface, we are stuck with the ugly mackie 
protocol to display information on Maschine MK3 displays. __WHAT A WASTE__


### Common Controls

__shift button__: restart button in the transport section is used for shited operations.  

---
__transport__:  
        
    play, stop, record, tap tempo and toggle metronome [transport section buttons. use shift 
    for metronome]

__recording__:

    record performace and automation [record and automation buttons, long press record
    button in arrangement view activates recording in overdub mode]

__track creation__:
    
    create and delete audio, return, and midi tracks [shift + console buttons: 1, 2, 3]
    (track deletion NotImplementedYet)

__auto arm__:

    auto arm midi track on selection

__note repeat__:

    note repeat with 8 rates straight and triplets (32t/32/16t/16/8t/8/4t/4) [use note repeat
    button to enable, and the 8 group buttons to select rate - default to 1/8]

__drum rack__:

    play drum racks and scroll drum cells up and down [step-chords buttons to scroll drum cells]
    when a drum rack has more than 16 pads to play, each cell page colors the pads differently.

__instrument__:

    play instruments in key with selectable keys and scales (NotImplementedYet)


#### Important Notes about the controller editor template

the controls in the attached controller editor template uses channel 16 to send and channels 2, 3 for
feedback.

all used controls "led on" section is set to "on midi in". this is necessary for midi feedback from Live
to Maschine MK3 controls. if a control is set to "on midi out" the control light will always respond to
presses instead of listening to Live for feedback.

the pads and group buttons and (secretly the sampling button) can multi colors. the "color mode" is set
to indexed so that these buttons can listen to the scripts and display correct skinning colors incoming
from Live.

Template offers 2 identical pages. one that displays information in mackie format. and one that displays
the maschine midi mode background. switch to page 2 to see information.

please keep that info in mind if you try to customize/relocate controls.