### nanometer configfile

#	General settings

MIDIChannel = 1
#	The MIDI channel number that the nanoKONTROL 2 uses to control the lights.
#	This must match the "Global MIDI Channel"-setting in the Korg Kontrol Editor.

TransportChan = 14
#	The MIDI channel used for the transport controls.
#	This must match the "Transport Button MIDI Channel" in the Korg Kontrol Editor.

SleepTimer  = 5
#	The number of minutes before the script enters lightshow-mode. 
#	Value can be between 0 (lightshow is disabled) to 300.

HighlightColor = -11835046
#	The color used for the marked mixer tracks.
#	The value is in RGBA format. Please read the documentation for more info.

MixerMode = True
#	True (Default) enables the Mixer mode.
#	Disable removes the Mixer mode.

ChannelrackMode = True
#	True (Default) enables the Channel rack mode.
#	Disable removes the Channel rack mode.

PlaylistMode = True
#	True (Default) enables the Playlist mode.
#	Disable removes the Playlist mode.

#	PeakMeter settings

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

#	Mixer settings

ArmedTracks = False
#	If set to True, the R-buttons will be used for arming tracks.
#	False (Default) will use the R-buttons for selecting tracks instead.

ExclusiveSelect = True
#	If set to True (Default), the R-buttons will select each track exclusivly.
#	False means that multiple tracks can be selected.

TrackRangeOnly = False
#	If set to True, the Track-buttons will only select tracks within the current range.
#	False (Default) lets the Track-buttons change between all the tracks in the mixer.

StickyMaster = False
#	If set to True, the master track will always be included in the track-range.
#	False (Default) will not include the master track.

ColoredRange = True
#	If set to True (Default), the mixer tracks controlled by the nanoKONTROL will be
#	highlighted in their own color. False disables the coloring.

BracketedRange = True
#	If set to True (Default), the mixer tracks controlled by the nanoKONTROL will
#	have brackets added to their names. False will leave the names untouched.

PickupValues = False
#	True (Default) means volume/panning will remain unchanged until the
#	fader/knob passes the last value it was set to. False disables this behaviour
#	and will cause the volume/panning to jump to the value set by the fader/knob.

TempoBase = 80
#	This sets the min (bottom)-value of the tempo-knob in the Playlist control mode.
#	The value can be between 10 and 397.


