import logging
import sys
import time
import csv
import os

from rtmidi.midiutil import open_midiinput, open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE

if getattr(sys, 'frozen', False): bundle_dir = os.path.dirname(sys.executable)  # we are running in a bundle
else: bundle_dir = os.path.dirname(os.path.abspath(__file__)) # we are running in a normal Python environment

submix_prev = 1
lcd_header = [240, 0, 0, 102, 20, 18]
midiconfig_path = os.path.join(bundle_dir, "MidiConfig.txt")
matrix_path = os.path.join(bundle_dir, 'totalmix_midi_mapping - matrix.csv')

with open(matrix_path, 'r') as f:
    matrix = list(csv.DictReader(f, delimiter=','))

output_CH_dict = matrix[2]
output_CC_dict = matrix[3]
output_submix_dict = matrix[4]
output_solo_dict = matrix[5]
output_mute_dict = matrix[6]
output_LCD_dict = matrix[7]
output_bank_dict = matrix[8]
data_list = [*matrix[-1].values()]

def _prompt_for_choice(question):
    """Prompt on the console for y/N."""
    return input("%s (y/N)\n" %question).strip().lower() in ['y', 'yes']


def change_row(next_row, current_pos, bank):


    change_row = True
    change_bank = True
    up = 0x29
    dn = 0x28
    bk_up = 0x2F
    bk_dn = 0x2E

    new_pos = current_pos
    print("next_row:", next_row, "current_pos:",current_pos, "change_row:", change_row)

    while True:

        if new_pos[:2] == next_row[:2]: change_row = False
        if new_pos[2:] == next_row[2:]: change_bank = False
        if current_pos == next_row: break

        if change_row:

            if next_row[:2] == "In" and current_pos[:2] == "Pb": command = up
            elif next_row[:2] == "Pb" and current_pos[:2] == "Ou": command = up
            elif next_row[:2] == "Ou" and current_pos[:2] == "In": command = up
            elif next_row[:2] == "In" and current_pos[:2] == "Ou": command = dn
            elif next_row[:2] == "Pb" and current_pos[:2] == "In": command = dn
            elif next_row[:2] == "Ou" and current_pos[:2] == "Pb": command = dn
            else: command = up

            midiout.send_message([NOTE_OFF | 0, command, 0])

            change_row = False

        if change_bank:

            if next_row[2:] < current_pos[2:]: command = bk_dn
            elif next_row[2:] > current_pos[2:]: command = bk_up
            else: command = bk_dn

            midiout.send_message([NOTE_OFF | 0, command, 0])

            change_bank = False


        msg_totalmix = midiin_totalmix.get_message()

        if msg_totalmix:

            message, deltatime = msg_totalmix

            if lcd_header == message[:6]:

                new_pos = ""
                for num in message[7:-1]: new_pos += chr(num)

                print("new_pos", new_pos, "\n")

                if new_pos == next_row: break

                else:
                    change_row = True
                    change_bank = True

        time.sleep(0.025)





    return new_pos










print("\n##########################################################################\nTotalMix Midi Mapping v0.1 (2024)\nOpen Source Midi Mapping for TotalMix from RME\nHacking the MackieControl-Implementation for absolute Midi Mapping.\nBuilt with python 3.9, python-rtmidi, pyinstaller\nAuthor: andreaseinsiedler\nhttps://github.com/andreaseinsiedler/totalmix_midi_mapping\n##########################################################################")

question = "Do you want to load the Midi settings from MidiConfig.txt?"
loading = _prompt_for_choice(question)

if loading:

    if os.path.exists(midiconfig_path):

        with open(midiconfig_path, "r") as f:

            ports_saved = [int(ele) for ele in list(f.read().splitlines())]
            print("Loaded from file:")
            print("Midi In External Port:", ports_saved[0])
            print("Midi In TotalMix Port:", ports_saved[1])
            print("Midi Out TotalMix Port:", ports_saved[2])

    else:
        print("Error: File MidiConfig.txt not found")
        loading = False

"""Midi Inputs Init"""

#log = logging.getLogger('midiin_poll')
#logging.basicConfig(level=logging.DEBUG)

#Midi Input from External

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

if not loading:
    print("\nChoose the external Input:")
    print("---------------------------\n")

port = None

try:
    if not loading: midiin_external, port_name_in_external = open_midiinput(port)
    if loading: midiin_external, port_name_in_external = open_midiinput(ports_saved[0])

except (EOFError, KeyboardInterrupt):
    sys.exit()

#Midi Input from TotalMix

if not loading:
    print("\nChoose the Input from TotalMix:\n")
    print("---------------------------\n")

port =  None

try:
    if not loading: midiin_totalmix, port_name_in_totalmix = open_midiinput(port)
    if loading: midiin_totalmix, port_name_in_totalmix = open_midiinput(ports_saved[1])
    midiin_totalmix.ignore_types(sysex=False)

except (EOFError, KeyboardInterrupt):
    sys.exit()

#Midi Output to Totalmix

#log = logging.getLogger('midiout')
#logging.basicConfig(level=logging.DEBUG)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

if not loading:
    print("\nChoose the output to TotalMix:\n")
    print("---------------------------\n")

port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    if not loading: midiout, port_name_out = open_midioutput(port)
    if loading: midiout, port_name_out = open_midioutput(ports_saved[2])

except (EOFError, KeyboardInterrupt):
    sys.exit()

print("\nMidi Input from External:", port_name_in_external)
print("Midi Input from TotalMix:", port_name_in_totalmix)
print("Midi Output to TotalMix: {}\n".format(port_name_out))

if not loading:
    question = "Do you want to save the midi settings?"
    saving = _prompt_for_choice(question)
else: saving = False

if saving:
    print("Here will be saving...")

    with open(midiconfig_path, "w") as text_file:
        text_file.write("%s\n%s\n%s\n" % (portin0, portin1, portout))


#Get LCD Text

midiout.send_message([0x80, 0x28, 0])

while True:

    msg_totalmix = midiin_totalmix.get_message()

    if msg_totalmix:

        message, deltatime = msg_totalmix

        if lcd_header == message[:6]:

            LCD_Text = ""
            for num in message[7:-1]: LCD_Text += chr(num)


            print("start LCD_Text", LCD_Text, "\n")

            break

    time.sleep(0.0025)

#Main

try:

    timer = time.time()

    while True:

        msg_external = midiin_external.get_message()
        msg_totalmix = midiin_totalmix.get_message()

        if msg_external:

            message, deltatime = msg_external

            send = True
            change_submix = False

            timer += deltatime
            #print("[%s] @%0.6f %r" % (port_name_in, timer, message))

            for row in matrix:

                if row["CC"]:

                    CH = int(row["Ch"])
                    CC = int(row["CC"])

                    if message[0] == CH+175 and message[1] == CC:

                        print("Input -> {} {} Ch: {} CC: {} Value: {}".format(row["Index"], row["Label"], CH, CC, message[2]))

                        routing_dict = dict(row)
                        for remove_key in ["Index", "Label", "M/S", "Ch", "CC", "Value"]: routing_dict.pop(remove_key, None)

                        for key, value in routing_dict.items():

                            if value:

                                output_ch = int(output_CH_dict[key])
                                if output_submix_dict[value]: submix = [int(e, 16) for e in output_submix_dict[value].split(",")]

                                if value == "TlkB":

                                    output_type = NOTE_OFF
                                    output_CC_or_Note = int(output_CC_dict[key], 16)
                                    print(message)
                                    output_type_string = "Note_Off"
                                    output_value = message[2]

                                    if message[2] > 0: send = True

                                    if message[2] == 0:
                                        if deltatime < 1: send = False
                                        else: send = True

                                        print("Button Held for :", deltatime)


                                elif value == "Map":

                                    output_CC_or_Note = int(output_CC_dict[key], 16)
                                    output_type_string = "Note_Off"
                                    output_value = message[2]
                                    if message[2] > 0:
                                        send = False
                                        output_type = NOTE_ON

                                    if message[2] == 0:
                                        output_type = NOTE_OFF
                                        send = True

                                elif value == "S" or value == "M":

                                    output_ch = int(output_CH_dict[value])
                                    totalmix_row = output_LCD_dict[key]
                                    totalmix_bank = output_bank_dict[key]

                                    print("before change row:", LCD_Text)
                                    LCD_Text = change_row(totalmix_row, LCD_Text ,totalmix_bank)
                                    print("after change row:", LCD_Text)

                                    if value == "S": output_CC_or_Note = int(output_solo_dict[key], 16)
                                    elif value == "M": output_CC_or_Note = int(output_mute_dict[key], 16)
                                    output_type = NOTE_OFF
                                    output_type_string = "Note_Off"
                                    output_value = 0
                                    bank = int(output_bank_dict[key])

                                else:

                                    output_type = CONTROL_CHANGE
                                    output_type_string = "CC"
                                    output_CC_or_Note = int(output_CC_dict[key])
                                    output_value = message[2]
                                    change_submix = True

                                if submix != submix_prev and change_submix:
                                    midiout.send_message(submix)
                                    submix_prev = submix

                                print("Submix -> ", value)

                                if send:
                                    print("Output -> {} Ch: {} {}: {} Value: {} \n".format(key, output_ch, output_type_string, output_CC_or_Note, output_value))
                                    msgout = ([output_type | output_ch, output_CC_or_Note, output_value])
                                    midiout.send_message(msgout)

                        break

        if msg_totalmix:

            message, deltatime = msg_totalmix

        time.sleep(0.0025)

except KeyboardInterrupt:
        print('')

finally:

    midiin_external.close_port()
    print("Midi In 1 closed")
    midiin_totalmix.close_port()
    print("Midi In 2 closed")
    del midiin_external
    del midiin_totalmix
    print("Exit.")





