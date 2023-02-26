### nanometer configfile
## Note: True and False must always begin with a capital letter!
 
# General settings

MIDIChannel = 1
#	The MIDI channel number that the nanoKONTROL 2 uses to control the lights.
#	This must match the "Global MIDI Channel"-setting in the Korg Kontrol Editor.

TransportChan = 14
#	The MIDI channel used for the transport controls.
#	This must match the "Transport Button MIDI Channel" in the Korg Kontrol Editor.

SleepTimer  = 5
#	The number of minutes before the script enters lightshow-mode. 
#	Value can be between 0 (lightshow is disabled) to 300.

PlayBlinkTempo = True
#   True (Default) will make the Play button flash in sync with the tempo when playing.
#   False will instead make the Record button flash in tempo sync during recording.

BlinkFullTempo = False
#	True will make the Play (or Record) button flash on full-tempo beat.
#	False (Default) will make the Play (or Record) button flash on half-tempo beat.

ModeBlink = True
#	True (Default) causes the transport-buttons to flash rapidly to indicate the
#	active mode when Cycle is pressed. False disables the flashing effect.

MixerMode = True
#	True (Default) enables the Mixer mode.
#	False disables the Mixer mode.

ChannelrackMode = True
#	True (Default) enables the Channel rack mode.
#	False disables the Channel rack mode.

PlaylistMode = True
#	True (Default) enables the Playlist mode.
#	False disables the Playlist mode.

ControllerLinkMode = False
#   True enables the Controller Link mode.
#   False (Default) disables the Controller Link mode.

# PeakMeter settings

PeakMeter = True
#	True (Default) enables the peak-meter.
#	If set to False, the peak-meter lights are disabled (Noo!!)

PlayingOnly = False
#	If set to True, the peak-meter will only be active while song/pattern is playing.
#	False (Default) means it's active all the time.

ReversePeak = False
#	If set to True, it reverses the nanometer (lights move from right to left).
#	False (Default) means the peak moves in the normal direction (left to right).

BigMeter = False
#	If set to True, both stereo and mono peak meters will be replaced by
#	a big peak meter that uses all the light buttons.

Clipping = True
#	True (Default) shows clipping of the signal if it goes above 0 dB.
#	If set to False, it disables the clip-light feature.

SelectedPeak = False
#	If set to True, the nanometer will show the peaks for the selected track.
#	If set to False (Default), it will show the peaks for the master track.

# Mixer settings

ArmedTracks = False
#	If set to True, the R-buttons will be used for arming tracks.
#	False (Default) will use the R-buttons for selecting tracks instead.

MultiSelect = False
#	If set to True, the R-buttons can be used to select multiple tracks.
#	False (Default) means that each track will be selected exclusively.

TrackRangeOnly = False
#	If set to True, the Track-buttons will only select tracks within the current range.
#	False (Default) lets the Track-buttons change between all the tracks in the mixer.

StickyMaster = False
#	If set to True, the master track will always be included in the track-range.
#	False (Default) will not include the master track.

RangeDisplayRect = True
#   If set to True (Default), the mixer tracks controlled by the nanoKONTROL will be
#   marked by a red rectangle. To use the ColoredRange option, this must be set to False.

RangeRectTimer = 0
# The number of seconds before the RangeRectDisplay rectangle is hidden.
# Value can be between 0 (Rectangle is always on) to 10.

ColoredRange = True
#	If set to True (Default), the mixer tracks controlled by the nanoKONTROL will be
#	colored by the script. False disables the coloring.

HighlightColor = -11835046
#	The color used for the marked mixer tracks.
#	The value is in RGBA format. Please read the documentation for more info.

BracketedRange = False
#	If set to True, the mixer tracks controlled by the nanoKONTROL will
#	have brackets added to their names. False (Default) will leave the names untouched.

PreserveMixDiff = False
#   If set to True, the faders of the selected tracks will stop when one of the faders
#   reach +5.6dB. False (Default) means all the faders can be raised to +5.6dB.

# Playlist settings

TempoBase = 80
#	This sets the min (bottom)-value of the tempo-knob in the Playlist control mode.
#	The value can be between 10 and 397.
