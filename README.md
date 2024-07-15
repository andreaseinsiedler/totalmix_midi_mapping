# totalmix_midi_mapping
Midi Mapping for RME TotalMix
(Version 1.0)

The Midi Implementation of TotalMix is based on Mackie Protocol, which makes it impossible to have absolute mappings, everything is relative and mapped in banks of 8.

Luckily the Channel Volumes and a couple of other very important functions are also implemented as plain MIDI, which makes it easier to map it to your Midi Controller.

The problem is, that if you map the Channel Volumes it always depends on the selected Submixes, what you are really controlling. 

With this Script you can map your Midi Controller to a Channel Volume for a specific Submix. It basically changes to the required Submix, before sending the Midi Data.

Installation:

Download the appropriate Zip-File for you OS.

For Windows: Start the Script with the Open_totalmix_midi_mapping_with_error_display.bat

For Mac: 

Usage:

The Mapping - Matrix is stored in a csv File (totalmix_midi_mapping - matrix.csv)
All the Midi Commands are also stored in a csv File (totalmix_midi_mapping - commands.csv)

For easier editing there are also xlsx versions of both files. There you have dropdown selection and color coding.



