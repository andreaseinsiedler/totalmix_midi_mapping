import logging
import sys
import time
import csv

from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
from rtmidi.midiconstants import (CONTROL_CHANGE)



def banking(row):

    #row = "Ou"
    send = True
    command = 0x28

    while True:

        if send:

            msgout = ([NOTE_OFF | 0, command, 0])

            midiout.send_message(msgout)

            send = False



        msg1 = midiin_1.get_message()



        if msg1:

            message, deltatime = msg1

            if lcd_header == message[:6]:

                ascii_char = ""
                for num in message[7:-1]: ascii_char += chr(num)


                print("LCD Text -> ", ascii_char, "\n")

                if ascii_char[:2] == row[:2]:
                    break

                else:
                    send = True

        time.sleep(0.0025)



with open('totalmix_midi_learn - matrix.csv') as f:
    matrix = list(csv.DictReader(f, delimiter=','))

output_CH_dict = matrix[2]
output_CC_dict = matrix[3]
output_submix_dict = matrix[4]
output_solo_dict = matrix[5]
output_mute_dict = matrix[6]
output_LCD_dict = matrix[7]
output_bank_dict = matrix[8]
#print(output_mute_dict)

submix_prev = 1
lcd_header = [240, 0, 0, 102, 20, 18]

#Midi Inputs Init

#log = logging.getLogger('midiin_poll')
#logging.basicConfig(level=logging.DEBUG)

#Midi Input External

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    #midiin_0, port_name_in_0 = open_midiinput(port)
    midiin_0, port_name_in_0 = open_midiinput(0)

except (EOFError, KeyboardInterrupt):
    sys.exit()

#Midi Input TotalMix Response

port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    #midiin_1, port_name_in_1 = open_midiinput(port)
    midiin_1, port_name_in_1 = open_midiinput(7)
    midiin_1.ignore_types(sysex=False)

except (EOFError, KeyboardInterrupt):
    sys.exit()

#Midi Output Init

#log = logging.getLogger('midiout')
#logging.basicConfig(level=logging.DEBUG)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    #midiout, port_name_out = open_midioutput(port)
    midiout, port_name_out = open_midioutput(7)

except (EOFError, KeyboardInterrupt):
    sys.exit()

print("\nMidi Input 1 (External):", port_name_in_0)
print("Midi Input 2 (TotalMix):", port_name_in_1)
print("Midi Output: {}\n".format(port_name_out))

try:

    timer = time.time()
    #print(timer)

    while True:

        msg0 = midiin_0.get_message()
        msg1 = midiin_1.get_message()

        if msg0:

            message, deltatime = msg0

            send = True


            timer += deltatime
            #print("[%s] @%0.6f %r" % (port_name_in, timer, message))

            for row in matrix:

                if (row["CC"]):

                    CH = int(row["Ch"])
                    CC = int(row["CC"])

                    if message[0] == CH+175 and message[1] == CC:

                        print("Input -> {} Ch: {} CC: {} Value: {}".format(row["Index"], CH, CC, message[2]))

                        routing_dict = dict(row)
                        for remove_key in ["Index", "Label", "M/S", "Ch", "CC", "Value"]: routing_dict.pop(remove_key, None)

                        for key, value in routing_dict.items():

                            if value:

                                output_ch = int(output_CH_dict[key])
                                submix = [int(ele, 16) for ele in output_submix_dict[value].split(",")]

                                if value == "Send":

                                    output_CC_or_Note = int(output_CC_dict[key], 16)
                                    print(message)
                                    output_type = "Note_Off"
                                    output_value = 0

                                    if message[2] > 0:
                                        send = True
                                        msgout = ([NOTE_OFF | output_ch, output_CC_or_Note, message[2]])


                                    if message[2] == 0:

                                        msgout = ([NOTE_OFF | output_ch, output_CC_or_Note, message[2]])

                                        if deltatime < 1:
                                            send = False
                                        else:
                                            send = True

                                        print(deltatime)


                                elif value == "Map":

                                    output_CC_or_Note = int(output_CC_dict[key], 16)
                                    output_type = "Note_Off"
                                    output_value = message[2]
                                    if message[2] > 0:
                                        send = False
                                        msgout = ([NOTE_ON | output_ch, output_CC_or_Note, message[2]])
                                    if message[2] == 0:
                                        msgout = ([NOTE_OFF | output_ch, output_CC_or_Note, message[2]])
                                        send = True

                                    #print("Map to {}".format(key))

                                elif value == "S" or value == "M":

                                    totalmix_row = output_LCD_dict[key]
                                    output_ch = 0

                                    banking(totalmix_row)

                                    if value == "S": output_CC_or_Note = int(output_solo_dict[key], 16)

                                    elif value == "M": output_CC_or_Note = int(output_mute_dict[key], 16)

                                    output_type = "Note_Off"
                                    output_value = 0
                                    bank = int(output_bank_dict[key])




                                    msgout = ([NOTE_OFF | output_ch, output_CC_or_Note, output_value])











                                else:

                                    output_CC_or_Note = int(output_CC_dict[key])
                                    output_type = "CC"
                                    output_value = message[2]

                                    msgout = ([CONTROL_CHANGE | output_ch, output_CC_or_Note, output_value])

                                if submix != submix_prev:
                                    midiout.send_message(submix)
                                    submix_prev = submix

                                print("Submix -> ", value)

                                if send:
                                    midiout.send_message(msgout)
                                    print("Output -> {} Ch: {} {}: {} Value: {} \n".format(key, output_ch, output_type, output_CC_or_Note, output_value))


                        break
        if msg1:

            message, deltatime = msg1



            #if message == [159, 127, 90]:
                #print("Midi In 2:", message, "<--Feedback Detection Pulse")


            if lcd_header == message[:6]:

                #sysex_msg_hex = []
                #for byte in message:
                #    sysex_msg_hex.append(hex(byte))
                #print("Midi In 2:", sysex_msg_hex, "<- -SYSEX")

                ascii_char = ""
                for num in message[7:-1]:
                    ascii_char += chr(num)
                print("LCD Text -> ", ascii_char, "\n")


            #else:
            #    print("Midi In 2:", message)





    time.sleep(0.0025)

except KeyboardInterrupt:
        print('')

finally:

    midiin_0.close_port()
    print("Midi In 1 closed")
    midiin_1.close_port()
    print("Midi In 2 closed")
    del midiin_0
    del midiin_1
    print("Exit.")







