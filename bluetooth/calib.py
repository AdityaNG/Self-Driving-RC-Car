from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event0')

#prints out device info at start
print(gamepad)

#evdev takes care of polling the controller in a loop
for event in gamepad.read_loop():
    if event.type!=0:
        #filters by event type
        print(type(event.code), event.code)
        if event.type == ecodes.EV_KEY:
            print("Button", event)
        elif event.code==5 or event.code==2:
            print("Right Joystick", event)
        elif event.code==0 or event.code==1:
            print("Left Joystick", event)
        elif event.code==16 or event.code==17:
            print("DPad", event)
        else:
            print("Unknown event", event)


