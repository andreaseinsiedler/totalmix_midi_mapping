import sys
import time
import csv
import os

from rtmidi.midiutil import open_midiinput, open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE