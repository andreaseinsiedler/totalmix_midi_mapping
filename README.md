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

For easier editing there are also xlsx versions of the matrix in the template folder. There you have dropdown selection and color coding.

The Matrix is expandable and you can tailor it to your needs both for your interface and your MIDI Controller.

The Script just work trough the matrix at every midi event and acts if it finds a binding to the received Channel and CC.

For Buttons you can define an ON Value that overrides the value what your MIDI Controller is sending.

In the xlsx template file, the is an example of an routing for a nanoKontrol2 to a Fireface 800. 