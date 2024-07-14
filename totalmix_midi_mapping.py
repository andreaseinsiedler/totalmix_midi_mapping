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
midiconfig_path = os.path.join(bundle_dir, "MidiConfig.txt")
matrix_path = os.path.join(bundle_dir, 'totalmix_midi_mapping - matrix.csv')
commands_path = os.path.join(bundle_dir, 'totalmix_midi_mapping - commands.csv')

with open(matrix_path, 'r') as f:
    matrix = list(csv.DictReader(f, delimiter=','))

with open(commands_path, 'r') as f:
    commands = list(csv.DictReader(f, delimiter=','))

print(commands[3])

output_CH_dict = commands[0]
output_CC_dict = commands[1]
output_submix_dict = commands[2]

'''Functions'''

def _prompt_for_choice(question):
    """Prompt on the console for y/N."""
    return input("%s (y/N)\n" %question).strip().lower() in ['y', 'yes']

'''Main'''

print("\n##########################################################################\nTotalMix Midi Mapping v0.1 (2024)\nOpen Source Midi Mapping for TotalMix from RME\nHacking the MackieControl-Implementation for absolute Midi Mapping.\nBuilt with python 3.9, python-rtmidi, pyinstaller\nAuthor: andreaseinsiedler\nhttps://github.com/andreaseinsiedler/totalmix_midi_mapping\n##########################################################################")

#Loading Midi Setup

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

#Saving Midi Setup

if not loading:
    question = "Do you want to save the midi settings?"
    saving = _prompt_for_choice(question)
else: saving = False

if saving:
    print("Here will be saving...")

    with open(midiconfig_path, "w") as text_file:
        text_file.write("%s\n%s\n%s\n" % (portin0, portin1, portout))


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

                        if row["Value"] and row["Value"] != "x" and message[2] != 0:
                            passed_value = int(row["Value"])
                        else: passed_value = message[2]


                        routing_dict = dict(row)
                        for remove_key in ["Index", "Label", "Ch", "CC", "Value"]: routing_dict.pop(remove_key, None)

                        for key, value in routing_dict.items():

                            if value:

                                output_ch = int(output_CH_dict[key])
                                if output_submix_dict[value]: submix = int(output_submix_dict[value], 16)

                                if value == "TlkB":

                                    output_type = NOTE_OFF
                                    output_CC_or_Note = int(output_CC_dict[key], 16)
                                    print(message)
                                    output_type_string = "Note_Off"
                                    output_value = passed_value

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


                                else:

                                    output_type = CONTROL_CHANGE
                                    output_type_string = "CC"
                                    output_CC_or_Note = int(output_CC_dict[key])
                                    output_value = passed_value

                                    change_submix = True


                                if change_submix:
                                    if submix != submix_prev:
                                        midiout.send_message([0xBC, submix, 50])
                                        time.sleep(0.05)
                                        submix_prev = submix

                                print("Submix -> ", value)

                                if send:
                                    print("Output -> {} Ch: {} {}: {} Value: {} \n".format(key, output_ch, output_type_string, output_CC_or_Note, output_value))
                                    msgout = ([output_type | output_ch, output_CC_or_Note, output_value])

                                    midiout.send_message(msgout)
                                    print(msgout)

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





