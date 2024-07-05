import logging
import sys
import time
import csv

from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
from rtmidi.midiconstants import (CONTROL_CHANGE)



with open('totalmix_midi_learn - matrix.csv') as f:
    matrix = list(csv.DictReader(f, delimiter=','))
    output_CH_dict = matrix[2]
    output_CC_dict = matrix[3]
    output_submix_dict = matrix[4]
    output_solo_dict = matrix[5]
    output_mute_dict = matrix[6]
    print(output_mute_dict)

submix_previous = 1

#Midi Input Init

#log = logging.getLogger('midiin_poll')
#logging.basicConfig(level=logging.DEBUG)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

#port = sys.argv[1] if len(sys.argv) > 1 else None

try:
   # midiin, port_name_in = open_midiinput(port)
    midiin, port_name_in = open_midiinput(0)
    port_name_in1 = port_name_in



except (EOFError, KeyboardInterrupt):
    sys.exit()


#Second Midi Input for TotalMix Response

#port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    # midiin, port_name_in = open_midiinput(port)
    midiin1, port_name_in = open_midiinput(5)
    port_name_in = port_name_in



except (EOFError, KeyboardInterrupt):
    sys.exit()

midiin.ignore_types(sysex=False)
midiin1.ignore_types(sysex=False)

#Midi Output Init

#log = logging.getLogger('midiout')
#logging.basicConfig(level=logging.DEBUG)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

#port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    #midiout, port_name_out = open_midioutput(port)
    midiout, port_name_out = open_midioutput(5)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("\nMidi Input1:", port_name_in1)
print("\nMidi Input2:", port_name_in)
print("Midi Output: {}\n".format(port_name_out))

try:

    timer = time.time()

    while True:

        msg = midiin.get_message()


        if msg:
            send = True
            banking = False
            message, deltatime = msg
            timer += deltatime
            #print("[%s] @%0.6f %r" % (port_name_in, timer, message))

            for row in matrix:

                if any (row["CC"]):

                    CH = int(row["Ch"])+175
                    CC = int(row["CC"])

                    if message[0] == CH and message[1] == CC:

                        print("Input -> {} {} {} {}".format(row["Index"], CH, CC, message[2]))

                        routing_dict = dict(row)
                        remove_keys = ["Index", "Label", "M/S", "Ch", "CC", "Value"]

                        for key in remove_keys:
                            routing_dict.pop(key, None)

                        for key, value in routing_dict.items():

                            if value:

                                print(key, value)

                                output_ch = int(output_CH_dict[key])


                                if value == "Map":

                                    output_CC_or_Note = int(output_CC_dict[key], 16)
                                    if message[2] > 0:
                                        send = False
                                        msgout = ([NOTE_ON | output_ch, output_CC_or_Note, message[2]])
                                    if message[2] == 0:
                                        msgout = ([NOTE_OFF | output_ch, output_CC_or_Note, message[2]])
                                        banking = True

                                    print("Map to {}".format(key))



                                elif value == "S" or value == "M":

                                    print("S or M")

                                    if value == "S":
                                        output_CC_or_Note = int(output_solo_dict[key], 16)

                                    elif value == "M":
                                        output_CC_or_Note = int(output_mute_dict[key], 16)

                                    msgout = ([NOTE_OFF | output_ch, output_CC_or_Note, 0])

                                    print("Output -> Channel: {} NOTE: {} Value: {} \n".format(output_ch,output_CC_or_Note,0))

                                else:
                                    print("else")
                                    print(output_CC_dict[key])
                                    output_CC_or_Note = int(output_CC_dict[key])
                                    msgout = ([CONTROL_CHANGE | output_ch, output_CC_or_Note, message[2]])
                                    print("Output -> Channel: {} CC: {} Value: {} \n".format(output_ch,output_CC_or_Note,message[2]))

                                submix = [int(ele, 16) for ele in output_submix_dict[value].split(",")]
                                print("Submix -> {}".format(output_submix_dict[value]))

                                if submix != submix_previous:
                                    print("Change Submix to {} {}".format(value, submix))
                                    midiout.send_message(submix)
                                    submix_previous = submix






                                if send:
                                    print("MSG OUT: ", msgout)
                                    midiout.send_message(msgout)


                                if banking:
                                    while True:

                                        msg1 = midiin1.get_message()

                                        if msg1:
                                            if msg1 [0] == [159, 127, 90]:
                                                print(msg1,"<--Feedback Detection Pulse")
                                            elif msg1 [0][0] == 240:
                                                print(msg1,"<- -SYSEX")
                                                ascii_char = ""
                                                for num in msg1[0][7:-1]:
                                                    ascii_char += chr(num)
                                                print(ascii_char)
                                                break
                                            else:
                                                print("MSG IN Port 2:", msg1[0])


                                    time.sleep(0.0025)
                        break

        time.sleep(0.0025)

except KeyboardInterrupt:
        print('')

finally:

    midiin.close_port()
    print("Midi In closed")
    midiin1.close_port()
    print("Midi In 2 closed")
    del midiin
    del midiin1
    print("Exit.")







