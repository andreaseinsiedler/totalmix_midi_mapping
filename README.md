# RME TotalMix Midi Mapping

Midi Mapping for RME TotalMix

The Midi Implementation of TotalMix is based on Mackie Protocol, which makes it impossible to have absolute mappings, everything is relative and mapped in banks of 8.

Luckily the Channel Volumes and a couple of other very important functions are also implemented as plain MIDI, which makes it easier to map it to your Midi Controller.

The problem is, that if you map the Channel Volumes it always depends on the selected Submixes, what you are really controlling. 

With this Script you can map your Midi Controller to a Channel Volume for a specific Submix. It basically changes to the required Submix, before sending the Midi Data.

## Installation:

Download the appropriate Zip-File for you OS and unzip it. 
- [Releases](https://github.com/andreaseinsiedler/totalmix_midi_mapping/releases) - latest builds of the script


The app is portable and should be started the following way:

for Windows: start the script with the Open_totalmix_midi_mapping_with_error_display.bat

for Mac: just start totalmix_midi_mapping

## Usage:

The Mapping - Matrix is stored in a csv File (totalmix_midi_mapping - matrix.csv)
All the Midi Commands are also stored in a csv File (totalmix_midi_mapping - commands.csv)

For easier editing there are also xlsx versions of both files. There you have dropdown selection and color coding.

-------------------------------------------

That's how far i got for now (10-2024). Its working for me right now, needs some proofing for normal users. 

Let me know if you are interested and i will get probably motivated to finish the beta release. 

If you know what your doing you can run it in pycharm and it works a treat, just clone the rep and get your setup into the matrix.

