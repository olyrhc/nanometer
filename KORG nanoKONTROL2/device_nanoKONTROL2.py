# name=nanometer (KORG nanoKONTROL2)
# url=https://github.com/olyrhc/nanometer

from ui import *
from midi import *
from channels import *
from device import *
from mixer import *
from arrangement import *
from transport import *
from general import *
from time import time
import config


def OnInit():
	print("*** nanometer script v1.1 by Robin Calvin (olyrhc) ***")
	global nm
	global kn
	nm = NanoMeter()
	kn = Kontrol()
	if config.PeakMeter: setHasMeters()

	
def OnDeInit():
	if config.BracketedRange: kn.rename_range(0)
	if config.ColoredRange: kn.set_range_color(1)


def OnControlChange(event):
	event.handled = True 					# Set the event as handled for now so it does not get sent to FL Studio unless we want it to
	button = event.data1
	mixer_range = kn.mixer_range
	master = config.StickyMaster
	highlight = config.ColoredRange
	faders = kn.faders
	knobs = kn.knobs
	track_select = kn.track_select
	markers = kn.markers
	transp_btns = kn.transp_btns
	mode = kn.current_mode

	if config.Debug: print("Id:",event.midiId, "Ch:",event.midiChan,"d1:",event.data1, "d2:", event.data2)		# Prints the recieved MIDI data to the 'Script output' window

	if event.data2 > 0:
	
		if button in kn.smr_tracks:	# Handle S,M,R buttons
			if nm.statuslights_ready():
				if mode == 0 and not kn.shift:
					track = kn.smr_tracks[button]
					if button in kn.smr('S'): soloTrack(track)
					elif button in kn.smr('M'): muteTrack(track)
					elif button in kn.smr('R'):
						if config.ArmedTracks: armTrack(track)
						elif config.ExclusiveSelect: setTrackNumber(track)
						else: selectTrack(track)
				elif mode == 1 and not kn.shift:
					nr = selectedChannel()
					if button == 19: soloChannel(nr)
					elif button == 20: muteChannel(nr)
				elif mode == 3 or kn.shift:
					if kn.shift: kn.shiftevent = True
					event.handled = False	# Pass the event to FL Studio
					kn.smr_press(event)

		elif button in faders:	# Handle mixer faders
			if mode == 0 and not kn.shift: kn.volume_fader(event.data1,event.data2)
			elif mode == 2 and not kn.shift: kn.playlist_zoom(event)
			elif mode == 3 or kn.shift:
				if kn.shift: kn.shiftevent = True
				event.handled = False

		elif button in knobs:	# Handle mixer knobs
			if mode == 0 and not kn.shift: kn.pan_knob(event.data1,event.data2)
			elif mode == 1 and not kn.shift: kn.set_target_mixer(event)
			elif mode == 2 and not kn.shift: kn.tempo_knob(event)
			elif mode == 3 or kn.shift:
				if kn.shift: kn.shiftevent = True
				event.handled = False

		elif button in track_select:	# Handle track-select buttons
			if not kn.shift:
				kn.set_repeat_event(button)
				if mode == 0:
					kn.sel_mixer(button)
				elif mode == 2:
					kn.playlist_nav(button)
			
		elif button in markers:	# Handle set and marker buttons
			if kn.shift:
				if mode == 0: kn.split_master(button)
				if mode == 2: kn.handle_markers(button)
			else:
				kn.set_repeat_event(button)
				if mode == 0: kn.move_range(event)
				elif mode == 1: kn.set_channel(button)
				elif mode == 2: kn.playlist_nav(button)

		elif button in transp_btns:
			if kn.shift:
				kn.quick_save(button)
			else:
				kn.set_transport(event)

		elif button == 2:
			kn.set_mode(event)

	elif event.data2 == 0:	# Handle button-release events

		kn.active[1] = True
	
		if button in track_select + markers:	# Track-select release
			if not kn.shift: del kn.repeat_event[button]
			
		elif button in transp_btns:	# Transport button release
			kn.set_transport(event)

		elif button == 2:
			kn.set_mode(event)
			
		elif mode == 3 or kn.shift:
			event.handled = False	# Pass the event to FL Studio
			kn.smr_press(event)


def OnIdle():
	mode = kn.current_mode
	flashrec = kn.flash_rec
	faderknob = kn.faderknob

	if kn.repeat_event:
		if mode == 0: kn.repeat_handler(0.3,0.18,kn.sel_mixer)
		if mode == 1: kn.repeat_handler(0.3,0.15,kn.set_channel)
		if mode == 2: kn.repeat_handler(0.4,0.1,kn.playlist_nav)

	if kn.loopmode:
		if time() - kn.loopmode > 0.7:
			setLoopMode()
			kn.loopmode = None

	if flashrec and flashrec <= 12:
		if flashrec % 2:	# Check if flash_rec is even
			kn.rectoggle ^= 1
			kn.toggle_rec_light(kn.rectoggle)
		kn.flash_rec += 1
		if flashrec == 12: kn.flash_rec = 0

	if faderknob[1] and time() - faderknob[0] < 3:
		kn.faderknob_focus()	# Focus the mixertrack if a fader/knob was moved
		kn.faderknob[1] = False
	elif time() - faderknob[0] >= 3 and faderknob[1] == False:
		kn.faderknob[1] = True

	if config.SleepTimer:
		if kn.active[1]:
			if time() - kn.active[0] > config.SleepTimer * 60:
				kn.pause(2)	# Abort pause animation
				if mode ==0: kn.set_track_status()	# Reset track lights
			kn.active[0] = time()
			kn.active[1] = False
		elif time() - kn.active[0] > config.SleepTimer * 60 and time() - kn.active[2] > 2:
			if getTrackPeaks(0,2) > 0: 
				kn.active[1] = True
				kn.active[0] = time()
			if not kn.active[1]: kn.pause(1)


def OnRefresh(flags):
	dirty_mix_sel = flags & HW_Dirty_Mixer_Sel
	dirty_mix_disp = flags & HW_Dirty_Mixer_Display
	dirty_mix_ctrl = flags & HW_Dirty_Mixer_Controls
	dirty_leds = flags & HW_Dirty_LEDs
	dirty_rlinks = flags & HW_Dirty_RemoteLinks
	dirty_perf = flags & HW_Dirty_Performance
	
	mode = kn.current_mode

	if config.SleepTimer:
		if dirty_mix_sel or dirty_mix_disp or dirty_mix_ctrl or dirty_leds:
			kn.active[1] = True

	if dirty_mix_sel and config.SelectedPeak:
		nm.track = trackNumber()

	if dirty_mix_ctrl and config.ColoredRange:	# Triggers on script-restart
		if not kn.init_range:
			if mode == 0:
				kn.clean_colors()
				kn.set_range_color()
	
	if mode == 0 and nm.statuslights_ready():
		if dirty_mix_sel and dirty_mix_ctrl: kn.set_track_status()	# Update the SMR lights when the mixer changes

	if dirty_leds:
		kn.set_transport_status()	# Update Play/Record lights when playing/record starts/stops
		if nm.statuslights_ready():
			if mode == 1: kn.channel_status()
	
	if dirty_mix_disp and config.BracketedRange:
		if mode == 0 and kn.no_brackets():	# Add brackets when a track inside the range changes name
			kn.rename_range(1)

	if dirty_rlinks and dirty_perf:	# Only triggered on start/reload of a project
		if config.Debug: print("Script re-initialized")
		if mode == 0:
			kn.set_mixer_range(1)
			kn.clean_colors()
			kn.set_range_color()
		kn.active[1] = True

	if config.Debug:
		#	These are kept for debugging purposes
		if flags & HW_Dirty_Mixer_Sel:	print("HW_Dirty_Mixer_Sel")
		if flags & HW_Dirty_Mixer_Display:	print("HW_Dirty_Mixer_Display")
		if flags & HW_Dirty_Mixer_Controls:	print("HW_Dirty_Mixer_Controls")
		if flags & HW_Dirty_RemoteLinks:	print("HW_Dirty_RemoteLinks")
		if flags & HW_Dirty_FocusedWindow:	print("HW_Dirty_FocusedWindow")
		if flags & HW_Dirty_Performance:	print("HW_Dirty_Performance")
		if flags & HW_Dirty_LEDs:	print("HW_Dirty_LEDs")
		if flags & HW_Dirty_RemoteLinkValues:	print("HW_Dirty_RemoteLinkValues")


def OnUpdateBeatIndicator(beat):
	if beat > 0:
		kn.rectoggle ^= 1
		kn.toggle_rec_light(kn.rectoggle)		# Toggle Rec-light on/off when recording

	
def OnUpdateMeters():
	if config.PeakMeter: nm.main()



class NanoMeter():

	def __init__(self):
		self.lights = ((19,20,21),(22,23,24),(25,26,27),(28,29,30),(31,32,33),(34,35,36),(37,38,39),(40,41,42))	# All the MIDI CC for the SMR light-buttons
		self.track = 0
		self.lastrow = 0
		self.maxedpeak = -50
		self.last_L, self.last_R = 0, 0
		self.volume = 0
		self.silence = 0
		self.lastmode = False
		self.clip_L, self.clip_R = None, None
		self.cliplight = [False,False]
		self.peak_list = self.create_peak_list(0)
		self.cc = MIDI_CONTROLCHANGE
		self.midichan = config.MIDIChannel - 1
		self.play = False
		self.clear = False


	def main(self):
	#	Here's where the fun stuff happens. It takes the current peak-signal and displays it across the light-rows of the SMR-buttons
		db = lambda x: -59.027+382.756*x+-2690.004*x**2+12192.951*x**3+-33120.365*x**4+54482.221*x**5+-53090.953*x**6+28161.016*x**7+-6258.646*x**8
		maxedpeak = self.maxedpeak
		last_L = self.last_L
		last_R = self.last_R
		L,R = None, None
		volume = getTrackVolume(0)
		wasplaying = self.play
		silenttime = self.silence
		lastmode = self.lastmode
		t = time()

		if config.BigMeter: peaks = (2,2)
		else: peaks = (0,1)
	
		peak_L = getTrackPeaks(self.track,peaks[0])
		peak_R = getTrackPeaks(self.track,peaks[1])
		peak_LR = db(getTrackPeaks(self.track,2))
		light_L = self.get_rows_from_peak(db(peak_L))
		light_R = self.get_rows_from_peak(db(peak_R))

		if peak_LR > maxedpeak:	# Detect the highest peak and adjust the meter-range accordingly
			self.peak_list = self.create_peak_list(peak_LR)
			self.maxedpeak = peak_LR

		if self.volume != volume:	# If the volume has changed, reset the highest detected peak
			self.maxedpeak = -50

		if peak_L + peak_R < 0.001 and silenttime == 0 and maxedpeak > -50:
			silenttime = time()
		elif silenttime > 0 and t - silenttime > 0.1:
			self.maxedpeak = -50
			silenttime = 0
			self.clear = False
			if not config.PlayingOnly:
				if config.Debug: print("Peaklight  reset")
				if kn.current_mode == 0: kn.set_track_status()
				elif kn.current_mode ==1: kn.channel_status()

		if peak_L + peak_R > 0.032 and peak_L == peak_R:	# If peak is not in stereo, change L and R
			if config.BigMeter: L = None
			else: L = 'M'
			R = None
		elif peak_L + peak_R > 0.032:
			L = 'S'	# Left = 'Solo' light-button
			R = 'R'	# Right = 'Record' light-button

		if not config.PlayingOnly or config.PlayingOnly and isPlaying():
			if L and L != lastmode:	# Mono/Stereo-mode was changed
				if config.Debug: print("Stereo/Mono mode changed")
				self.set_light(8,1,0)		# Clear all the lights
				last_L = 0	# Trigger a complete redraw of  the next Left light row
				last_R = 0	# ...and the same for the next Right light row

		if self.statuslights_ready():
			if wasplaying and not isPlaying():
				self.set_light(8,1,0)	# Clear all the lights when playing stops
				if kn.current_mode == 0: kn.set_track_status()
				elif kn.current_mode ==1: kn.channel_status()
				if config.Debug: print("Peaklight  reset")
		else:
			if config.Clipping:
				if self.clipping(peak_L,0):	# Handle clipping for left or mono peak
					if last_L == 8: last_L -= 1
				elif self.cliplight[0]: 
					if L: self.set_light(8,8,0,'S')	# Deactivate clip-lights for left/mono channels
					else: self.set_light(8,8,0)
					self.cliplight[0] = False
				if self.clipping(peak_R,1):	# Handle clipping for right peak
					if last_R == 8: last_R -= 1
				elif self.cliplight[1]:
					if R: self.set_light(8,8,0,'R')
					else: self.set_light(8,8,0)
					self.cliplight[1] = False

			if not config.PlayingOnly:
				if peak_L + peak_R > 0.01:	# Clear all the lights just before the meter starts
					if  not self.clear:
						self.set_light(1,8,0)
						self.clear = True
			elif not wasplaying and isPlaying():
						self.set_light(1,8,0)
						last_L = 0
						last_R = 0

			if light_L > last_L:	# Let there be light! (left peak and mono)
				self.set_light(last_L,light_L,1,L)
			elif light_L < last_L:
				self.set_light(last_L,light_L,0,L)

			if R:	# Only bother with right channel if we're in stereo mode
				if light_R > last_R:	# Lights for right peak
					self.set_light(last_R,light_R,1,R)
				elif light_R < last_R:
					self.set_light(last_R,light_R,0,R)

		self.last_L= light_L
		self.last_R= light_R
		self.volume = volume
		if L: self.lastmode = L
		self.play = isPlaying()
		self.silence = silenttime


	def get_rows_from_peak(self,db_peak,peak_list=None):
	# get_rows_from_peak takes a peak-signal value and compares it against a ranged list of peak-values to find the closest match. The closest matching value is then used to determine the number of vertical rows (light-groups) that the peak-signal corresponds to. The returned number is between 0 and 8.
	#
	# The 'db_peak' argument is the peak-signal value
	# The 'peak_list' argument is optional. If omitted, it uses the default list that ranges from -48dB to 0dB.

		if not peak_list: peak_list = self.peak_list
		
		abs_diff = lambda list_value : abs(list_value - db_peak)
		closest_value = min(peak_list, key=abs_diff)
		return peak_list.index(closest_value)


	def create_peak_list(self,db_peak):
	# 'create_peak_list' generates "peak lists" that are used by the 'get_rows_from_peak'-method. These lists contain 9 values. The first value roughly equals -48db on the peak-meter and the following values are then placed at various intervals by the values from the 'span' list.
	#
	# Note: The 'span' list is used as a template for the sensitivity-scale for the lights on the nanoKontrol. The first values are set 2.5dB apart to make the lights more reactive at the top of the peak-signal (assuming we have a max-peak of 0dB). The following values are placed further apart as the signal becomes weaker. The distance between these values is relative to the signal and will be recalculated to make them fit within the given meter-range (-48dB up to 'n' dB as determined by the 'db_peak' argument).

		span = [2.5, 2.5, 2.5, 5.0, 5.0, 7.5, 7.5, 15.5]	# span list, 48dB range
		if db_peak < -45: db_peak = -45	# Range must not be smaller than (-48 to -45dB)
		x = (-48 - db_peak) / -48	# Calculate the new distance between the light-points
		newspan = [x * i for i in span]
		dblist = []
		for i in span:	# Generate a new peak-list
			dblist.append(db_peak - sum(newspan))
			newspan.pop()
		dblist.append(db_peak)
		return dblist


	def clipping(self,peak,mode):
	#	Determine if the signal is clipping and activate the clip-light
		if type(peak) is not float: raise TypeError("peak argument must be of type 'float'")
		if type(mode) is not int: raise TypeError("mode argument must be of type 'int'")
		if mode not in range(0,2): raise ValueError("mode argument must be '1' or '2'")

		t = time()
		clip = [self.clip_L, self.clip_R]
		last = [self.last_L, self.last_R]
		
		if peak > 1:	# Check if peak signal is clipping
			clip[mode] = [t]
			self.cliplight[mode] = True
		elif peak < 1 and clip[mode] and len(clip[mode]) < 3:	# Leave the clip-light on for 3 seconds
			if t - clip[mode][-1] >= 1: clip[mode].append(t)
			if last[mode] > 7: last[mode] = 7
		elif peak < 1 and clip[mode] and len(clip[mode]) > 2:	# Time is up -> clipping() is finished
			clip[mode] = None

		if mode == 0:	#  Update the attributes with the data we changed
			self.clip_L = clip[0]
			self.last_L = last[0]
		elif mode == 1:
			self.clip_R = clip[1]
			self.last_R = last[1]

		if clip[mode]: return True
		else: return False


	def set_light(self,start_row, end_row, state, light = None):
	# "set_light" uses device.midiOutMsg to adress the Mute/Solo/Record light-buttons on the Korg nanoKontrol 2.
	#
	# The 'start_row' and 'end_row' arguments takes a number between 1 to 8 (or 8 to 1) and changes the state of the light-buttons in the given range.
	# The 'state' argument takes a bool-value. If it evaluates to true, the lights are set to their active (lit) state. A false value turns the lights off instead.
	# The 'light' argument is optional. Must be in string-format and accepts  'S', 'M' or 'R'. It targets the respective light-button (Solo, Mute, Record). If omitted, all three buttons are targeted simultaneously.
	
		start_row = start_row or 1
		if config.ReversePeak: lights = self.lights[::-1]		#	Lights go in reverse direction
		else: lights = self.lights
		chan = self.midichan
		cc = self.cc
		smr = 'SMR'

		if light and len(light) == 1:
			if light in smr: button = smr.index(light)	# Set button to 0, 1 or 2
			else: light = None

		if state:	vel=127
		else: 	vel=0
	
		if end_row == 0:
			end_row = 1
			vel=0

		if	end_row < start_row:
			start_row, end_row = end_row, start_row
			rows = range(start_row-1,end_row)[::-1]
		else:	rows = range(start_row-1,end_row)

		for row in rows:
			if not light:
				for button in lights[row]:
					midiOutMsg(cc,chan,button,vel)	# Activate all three lights
			else: midiOutMsg(cc,chan,lights[row][button],vel)	# Activate one light (S, M or R)


	def statuslights_ready(self):
	#	Returns True if the SMR status-lights are ready, i.e. the lights are not busy with the peak meter
		if config.PlayingOnly and not isPlaying(): return True
		elif not config.PlayingOnly:
			if getTrackPeaks(self.track,2) < 0.001: return True
		return False



class Kontrol():

	def __init__(self):
		self.tracks = []
		self.smr_tracks = {}
		self.mixer_range = []
		self.set_mixer_range(1)
		self.repeat_event = {}		
		self.defaultcolors = {}
		self.init_range = False
		self.modes = self.get_modes(0)
		self.current_mode = self.get_modes(1)
		self.lastzoom_x, self.lastzoom_y = 0, 0
		self.lastfocus = 2
		self.lastknob = 0
		self.faderknob = [0,1]
		self.rectoggle = 0
		self.shift = False
		self.shiftevent = False
		self.active = [time(),True,0]
		self.flash_rec = 0
		self.loopmode = None
		self.track_select = (0,1)					# Track buttons cc codes
		self.markers = (3,4,5)						# Marker buttons cc codes
		self.transp_btns = (6,7,8,9,10)			# Transport buttons cc codes
		self.knobs = (11,12,13,14,15,16,17,18)		# Knobs cc codes
		self.smr_btns = [i for i in range(19,43)]
		self.faders = (43,44,45,46,47,48,49,50)	# Faders cc codes
		if getVersion() >= 13: self.pickup = True
		else: self.pickup = False

	def smr(self,key):
	#	Generates a list of numbers that match the CC codes for the S, M or R buttons
		SMR = 'SMR'
		if key in SMR:
			if key == SMR[0]: k = 1
			elif key == SMR[1]: k = 2
			elif key == SMR[2]: k = 3
			else: raise ValueError("key argument must be one of the strings 'S', 'M' or 'R'")
		r = [3 * x + k for x in range(6,14)]
		return r


	def set_track_status(self):
	#	This is used to update the lights of the Solo, Mute and Record buttons
		smr_tracks = self.smr_tracks
		buttons = self.smr_btns
		cc = MIDI_CONTROLCHANGE
		chan = config.MIDIChannel - 1

		for button in buttons:	# Clear all lights
			midiOutMsg(cc,chan,button,0)

		for button in buttons:	# Activate the buttons light if the corresponding mixer state is set
			track = smr_tracks[button]
			if button in self.smr('S'):
				if isTrackSolo(track): midiOutMsg(cc,chan,button,127)
			elif button in self.smr('M'):
				if isTrackMuted(track): midiOutMsg(cc,chan,button,127)
			elif button in self.smr('R'):
				if config.ArmedTracks: sel_arm = isTrackArmed(track)
				else: sel_arm = isTrackSelected(track)
				if sel_arm: midiOutMsg(cc,chan,button,127)


	def volume_fader(self,fader,val):
	#	This takes the input from the nanoKontrol faders and use it to set the volume
		faderlist = self.faders
		mixer_range = self.mixer_range
		n = faderlist.index(fader)
		track = mixer_range[n]
		volume = val / 127 - 0.003
		current = getTrackVolume(track) * 127
		if self.pickup: setTrackVolume(track,volume,2)
		else: setTrackVolume(track,volume)
		if track > 0: self.faderknob[0] = time()


	def pan_knob(self,knob,val):
	#	This takes the input from the nanoKontrol knobs and use it to set the panning
		knoblist = self.knobs
		mixer_range = self.mixer_range
		n = knoblist.index(knob)
		track = mixer_range[n]
		pan = val / 127 * 2 - 1.008
		pval = getTrackPan(track) * 64
		current = round(pval + 64)
		if self.pickup: setTrackPan(track,pan,2)
		else: setTrackPan(track,pan)
		if track > 0: self.faderknob[0] = time()


	def set_transport(self,event):
	#	Handles the control of the transport buttons
		transp_btns = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = event.midiChan
		button = event.data1
		vel = event.data2
		
		if button == transp_btns[0]:					# Rewind
			if vel == 127: rewind(2,15)
			elif vel == 0: rewind(0,15)
			midiOutMsg(cc,chan,button,vel)
		elif button == transp_btns[1]:				# FForward
			if vel == 127: fastForward(2,15)
			elif vel == 0: fastForward(0,15)
			midiOutMsg(cc,chan,button,vel)
		elif button == transp_btns[2]:				# Stop
			if vel == 127:
				stop()
				self.loopmode = time()	# Register the time of the keypress for the loopmode event
			elif vel == 0: self.loopmode = None	# Clear the loopmode event
			midiOutMsg(cc,chan,button,vel)
			kn.rectoggle = 0		# Reset rectoggle

		elif button == transp_btns[3] and vel == 127: start()		# Play
		elif button == transp_btns[4] and vel == 127: record()	# Record


	def set_transport_status(self):
	#	Detects if Play or Record is activated and toggles their lights
		light = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = config.TransportChan -1

		if isPlaying(): midiOutMsg(cc,chan,light[3],127)
		else: midiOutMsg(cc,chan,light[3],0)

		if isRecording(): midiOutMsg(cc,chan,light[4],127)
		else: midiOutMsg(cc,chan,light[4],0)


	def toggle_rec_light(self,state):
	#	This is used to toggle (blink) the light of the Record-button while recording
		light = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = config.TransportChan -1
		
		if isPlaying() and isRecording() or self.flash_rec:
			if state: midiOutMsg(cc,chan,light[4],127)
			else: midiOutMsg(cc,chan,light[4],0)


	def set_mixer_range(self,start):
	#	This generate lists of which tracks are currently controlled
		mixdict = {}		

		if start not in range(0,120): raise ValueError("start argument must be a number between 0-119")
		if not config.StickyMaster:
			mixer = [i for i in range(start,start+8)]	# Generate a list of 8 mixer tracks
			smr_mixer = [i for i in range(start,start+8) for n in range(3)]	# duplicate each track 3 times ('S'+'M'+'R')
					
		else:
			mixer = [0] + [i for i in range(start,start+7)]	# Same as above but start with master track and add 7 tracks
			smr_mixer = [0,0,0] + [i for i in range(start,start+7) for n in range(3)]
		for button, track in enumerate(smr_mixer,19):	#	Use enumerate() to replicate the button numbers
			mixdict[button] = track	# Create a dictionary with buttons as keys and mixer-tracks as values
		self.mixer_range = mixer
		self.smr_tracks = mixdict


	def sel_mixer(self,direction):
	#	This takes input from the track-buttons and use it to select tracks
		mixer_range = self.mixer_range
		master = config.StickyMaster
		move = None
		if direction == 0: move = -1
		elif direction == 1: move = 1
		if not move: return
		selected = trackNumber()

		if config.TrackRangeOnly:
			if master and move == 1 and selected == mixer_range[0]:	# from master to first
				setTrackNumber(mixer_range[1],1)
			elif master and move == -1 and selected == mixer_range[1]:	# from first to master
				setTrackNumber(mixer_range[0])

			elif move == 1 and selected == mixer_range[-1]:	# From last to first
				setTrackNumber(mixer_range[0],1)
			elif move == -1 and selected == mixer_range[0]:	# from first to last
				setTrackNumber(mixer_range[-1],1)

			elif selected not in mixer_range:	# if outside range, go to first
				setTrackNumber(mixer_range[0],1)
			elif move == 1: setTrackNumber(selected +1,1)	# move to next
			elif move == -1: setTrackNumber(selected -1,1)	#move to previous
		else:
			if move == 1:
				if selected == 126: setTrackNumber(0)
				else: setTrackNumber(selected +1,1)	# move to next
			elif move == -1:
				if selected == 0: setTrackNumber(126)
				else: setTrackNumber(selected -1,1)	#move to previous


	def set_range_color(self,state=None):
	#	This is used to change or update the color of the tracks that are controlled
		mixer_range = self.mixer_range
		marked = config.HighlightColor
		umarked = -10261391
		found_marked = False
		mark_count = 0
		if config.StickyMaster: clear_idx = 1
		else: clear_idx = 0

		def  defaultColor(track):
			if track in self.defaultcolors: color = self.defaultcolors[track]
			else: color = umarked
			return color

		if not state:
			self.defaultcolors = {}
			for track in mixer_range:
				color = getTrackColor(track)
				if color != umarked and color != marked: self.defaultcolors[track] = color
			if config.StickyMaster: r1 = mixer_range[1]
			else: r1 = mixer_range[0]
			try: setTrackNumber(r1,1)
			except: pass
			
			for track in mixer_range:
				color = getTrackColor(track)
				if color != marked:
					try: setTrackColor(track,marked)
					except: pass
			
			for track in mixer_range:
				color = getTrackColor(track)
				if color == marked: mark_count +=1
			if mark_count == 8: self.init_range = True	# Flag that coloring is done
			else:
				self.init_range = False
				if config.Debug: print("marked tracks found:",mark_count)

		elif state ==1:	# Reset all mixer colors
			for track in mixer_range:
				color = defaultColor(track)
				setTrackColor(track,color)

		elif state > 1:
			if state == 2:	# Update colors for decreasing range
				clear_track = mixer_range[-1] +1
				mark_track = mixer_range[clear_idx]
			if state == 3:	# Update colors for inreasing range
				clear_track = mixer_range[clear_idx] -1
				mark_track = mixer_range[-1]
			setTrackColor(clear_track,defaultColor(clear_track))
			color = getTrackColor(mark_track)
			if color != umarked and color != marked: self.defaultcolors[mark_track] = color	# Store the default color
			setTrackColor(mark_track,marked)


	def clean_colors(self):
	#	Resets the default colors (where necessary) for all the mixer-tracks
		marked = config.HighlightColor
		default = -10261391
		
		for track in range(126):
			try:
				color = getTrackColor(track)
				if color == marked: setTrackColor(track,default)
			except: pass


	def rename_range(self,state):
	#	This is used to add brackets to the names of the mixer tracks that are currently controlled
		mixer_range = self.mixer_range
		master = config.StickyMaster
		
		if config.BracketedRange:
			for track in mixer_range:
				n = getTrackName(track)
				name = None
				if state == 1:	# Rename whole range
					if n[0] != "[" and n[-1] != "]": name = "[" + n + "]"
				elif not state:	# Clear whole range
					if n[0] == "[" and n[-1] == "]": name = n[1:-1]
				try:
					if name: setTrackName(track,name)
				except: pass		# Avoid a script-crash in case FL Studio is busy and throws an error

			if state ==2:		# clear rightmost track
				track = mixer_range[-1] +1
			elif state == 3:	# clear leftmost track
				if master: idx = 1
				else: idx = 0
				track = mixer_range[idx] -1
			try:
				if state > 1:
					n = getTrackName(track)
					if n[0] == "[" and n[-1] == "]": name = n[1:-1]
					if name: setTrackName(track,name)
			except: pass


	def no_brackets(self):
	#	This checks if the current track-name has brackets or not
		track = trackNumber()
		if track in self.mixer_range:
			name = getTrackName(track)
			if name[0] != "[" and name[-1] != "]": return True
			else: return False
		return False


	def move_range(self,event):
	# Handle movement of the controlled mixer tracks
		mixer_range = self.mixer_range
		markers = self.markers
		master = config.StickyMaster
		highlight = config.ColoredRange
		brackets = config.BracketedRange
		mode = self.current_mode

		if master: track = mixer_range[1]
		else: track = mixer_range[0]

		if event.data1 == markers[0]:	# Set-button
			track = trackNumber()
			if master and track < 1 or track > 119: return	# Prevent the track-range from being moved too far
			elif not master and track > 118: return
			else:
				if highlight: self.set_range_color(1)
				if brackets: self.rename_range(0)
				self.set_mixer_range(track)
				setTrackNumber(self.mixer_range[-1],1)
				setTrackNumber(track,1)
				if highlight: self.set_range_color()

		elif event.data1 == markers[1]:	# Marker prev-button
			track -= 1
			if master and track < 1: pass
			elif not master and track < 0: pass
			else:
				self.set_mixer_range(track)
				if highlight: self.set_range_color(2)
				if brackets:
					self.rename_range(2)
				if master: idx = 1
				else: idx = 0
				setTrackNumber(mixer_range[-1] -1,1)
				setTrackNumber(mixer_range[idx] -1,1)
					
		elif event.data1 == markers[2]:	# Marker next-button
			track += 1
			if master and track < 1 or track > 119: return	# Prevent the track-range from being moved too far
			elif not master and track > 118: return
			else:
				self.set_mixer_range(track)
				if highlight: self.set_range_color(3)
				if brackets:
					self.rename_range(3)	# clear brackets to the left of the range
					self.rename_range(1)	# update brackets to include the new track
				setTrackNumber(mixer_range[-1] +1,1)
				setTrackNumber(track,1)


	def split_master(self,button):
		self.shiftevent = True
		marked = config.HighlightColor
		umarked = -10261391
		mixer_range = self.mixer_range
		markers = self.markers
		highlight = config.ColoredRange
		brackets = config.BracketedRange
		master = config.StickyMaster
		skip = False

		if self.shift and button == markers[0]:
			if master:
				um, m = 0,  -1
				setTrackNumber(mixer_range[1],1)
			else:
				um, m = -1, 0
				setTrackNumber(mixer_range[0],1)
				if self.mixer_range[0] == 0: skip = True

			if not skip:
				if brackets:
					name = False
					n = getTrackName(mixer_range[um])
					if n[0] == "[" and n[-1] == "]": name = n[1:-1]
					if name: setTrackName(mixer_range[um],name)
				if highlight: setTrackColor(mixer_range[um],umarked)

			if master == True: config.StickyMaster = False
			elif master == False: config.StickyMaster = True
			if skip: setTrackNumber(1,1)
			self.set_mixer_range(trackNumber())
			if highlight: setTrackColor(self.mixer_range[m],marked)
			if brackets:
				name = False
				n = getTrackName(self.mixer_range[m])
				if n[0] != "[" and n[-1] != "]": name = "[" + n + "]"
				if name: setTrackName(self.mixer_range[m],name)


	def set_mode(self,event):
	#	This switches between the Mixer, Channel rack and Playlist modes
		cc = MIDI_CONTROLCHANGE
		chan = event.midiChan
		smr_chan = config.MIDIChannel - 1
		highlight = config.ColoredRange
		brackets = config.BracketedRange
		smr_lights = self.smr_btns
		button = event.data1
		vel = event.data2
		windows = ('Mixer','Channel rack','Playlist/Pianoroll','Controller Link mode')
		mode = self.current_mode
		modes = self.modes
		cc = MIDI_CONTROLCHANGE
		peaks = getTrackPeaks(nm.track,2)

		if len(self.modes) == 0: return	# Break if all modes are disabled in the configfile

		if vel == 127: self.shift = True	# Register as a shift-button when pressed down
		else: self.shift = False

		if vel == 0 and not self.shiftevent:
			i = modes.index(mode)
			if i + 1 < len(modes): mode = modes[i + 1]
			else: mode = modes[0]
			
			if mode == 0:
				if brackets: self.rename_range(1)	# Add brackets to names
				if highlight: self.set_range_color()	# Set range colors
				if peaks < 0.01: self.set_track_status()
			elif mode > 0 and 0 in modes:
				if highlight: self.set_range_color(1)	# Clear range colors
				if brackets: self.rename_range(0)
				if peaks < 0.01:
					for light in smr_lights:	# Clear all lights
						midiOutMsg(cc,smr_chan,light,0)
					if mode == 1: self.channel_status()

			showWindow(mode)
			setHintMsg(windows[mode])
			self.current_mode = mode
				
		self.shiftevent = False
		midiOutMsg(cc,chan,button,vel)


	def set_channel(self,button):
	#	Navigates between channels using the marker buttons
		markers = self.markers

		if button == markers[0]:	# marker set
			channel = selectedChannel()
			showEditor(channel)

		if button ==  markers[1]:	# marker prev
			globalTransport(102,-1,2,15)
			
		elif button == markers[2]:	# marker next
			globalTransport(102,1,2,15)
			
		nr = selectedChannel()
		name = getChannelName(nr)
		setHintMsg(name)


	def channel_status(self):
	#	Sets the Solo/Mute lights to the status of the current channel
		cc = MIDI_CONTROLCHANGE
		smr_chan = config.MIDIChannel - 1
		solo_light = 19
		mute_light = 20
		solo, mute = 0, 0
		nr = selectedChannel()
		if isChannelSolo(nr): solo = 127
		if isChannelMuted(nr): mute = 127
		midiOutMsg(cc,smr_chan,solo_light,solo)
		midiOutMsg(cc,smr_chan,mute_light,mute)


	def set_target_mixer(self,event):
	#	Changes the target mixer track for the current channel
		vel = event.data2
		knobs = self.knobs
		channel = selectedChannel()

		if event.data1 == knobs[0]:	# First knob
			current = getTargetFxTrack(channel)
			track = vel - 1
			if track > 125: track = 125
			if abs(track - current) == 1:
				setTrackNumber(track,1)
				name = getTrackName(track)
				linkTrackToChannel(0)		# linkTrackToChannel() messes up the track name... :(
				setTrackName(track,name)	# ...so let's change it back again.


	def playlist_nav(self,direction):
	#	Navigates the playlist/pianoroll
		track_select = self.track_select
		markers = self.markers
		playlist = getFocused(2)
		pianoroll = getFocused(3)

		if playlist or pianoroll:
			if direction == track_select[0]:
				globalTransport(100,-1,2,15)
			elif direction == track_select[1]:
				globalTransport(100,1,2,15)
			if direction == markers[0]:
				visible = getVisible(3)
				focused = getFocused(3)
				if visible and not focused: setFocused(3)
				elif not visible: showWindow(3)
				else: hideWindow(3)
			elif direction == markers[1]:
				jump = jumpToMarker(-1,0)
				if jump == -1: jog(-1)	# If no markers, jump to next bar instead
			elif direction == markers[2]:
				jump = jumpToMarker(1,0)
				if jump == -1: jog(1)
			if playlist: self.lastfocus = 2
			else: self.lastfocus = 3


	def playlist_zoom(self,event):
	#	Handles the horizontal/vertical zooming of the playlist
		vel = event.data2
		faders = self.faders
		lzx = self.lastzoom_x
		lzy = self.lastzoom_y

		if not getFocused(2) and not getFocused(3):
			return	# Don't do anything if playlist or pianoroll is not focused!

		if event.data1 == faders[0]:		# First fader
			if vel >= lzx + 3:	# Zoom in, fader-throw resolution set to 3 (slow)
				jog(0)
				horZoom(1)
				self.lastzoom_x = vel
			elif vel <= lzx:
				if vel < 20: res = 2	# If throw is small , zoom-out needs to be slightly quicker, resolution set to 2
				else: res = 3
				if vel <= lzx - res:
					jog(0)
					horZoom(-1)
					self.lastzoom_x = vel

		elif event.data1 == faders[1]:	# Second fader
			if vel > lzy:
				verZoom(1)
				self.lastzoom_y = vel
			elif vel < lzy:
				verZoom(-1)
				self.lastzoom_y = vel


	def tempo_knob(self,event):
	#	Changes the current tempo
		knob = event.data1
		knobval = event.data2
		lastknob = self.lastknob
		newtempo = 0
		tempo = int(getCurrentTempo(1))
		base = config.TempoBase - 2
		catch = 2

		if knob == self.knobs[0]:
			t = knobval - lastknob
			pos = base + knobval - tempo
			if t < 0 and pos < -1: catch = 4
			elif t > 0 and pos > 1: catch = 4
			if abs(base + knobval - tempo) < catch:
				if t > 0 and tempo <= base+126: newtempo = 10
				elif t < 0 and tempo >= base: newtempo = -10
		
		if newtempo:
			if tempo == config.TempoBase and newtempo < 0: pass
			else: globalTransport(105,newtempo,2,15) 
		self.lastknob = knobval


	def repeat_handler(self,delay,repeat,function):
	# 	Handles the repeat-event when a button is held down
		current_time = time()
		repeat_event = self.repeat_event
		
		for button in self.repeat_event:
			press_time = repeat_event[button][0]
			last_repeat = repeat_event[button][1]
			if current_time - press_time > delay:
				if current_time - last_repeat > repeat:
					function(button)
					self.repeat_event[button] = (press_time,time())

	
	def set_repeat_event(self,button):
	# 	Registers that a button needs to be repeated
		self.repeat_event[button] = (time(),0)


	def faderknob_focus(self):
	#	Uses setTrackNumber() to scroll the mixer to the tracks of the controlled range	
		if config.StickyMaster: t = 1
		else: t = 0
		selected = trackNumber()
		setTrackNumber(self.mixer_range[t],1)
		setTrackNumber(self.mixer_range[7],1)
		setTrackNumber(selected)


	def handle_markers(self,button):
	#	Creates and jumps between markers in the playlist
		markers = self.markers
		self.shiftevent = True
		name = "Marker #"
		names = []
		taken = True
		nr = 1
		x=0

		while True:	# Create a list with all the used marker names
			m = getMarkerName(x)
			if not m: break
			names.append(m)
			x += 1

		while name + str(nr) in names: nr +=1	# Check for the next available name

		if button == markers[0]:
			ct = currentTime(0)
			addAutoTimeMarker(ct,name + str(nr))
		elif button == markers[1]:
			jumpToMarker(-1,0)
		elif button == markers[2]:
			jumpToMarker(+1,0)


	def quick_save(self,button):
	#	Saves the project without highlighted mixer-colors!
		self.shiftevent = True
		mixermode = False
		if self.current_mode == 0: mixermode = True
		
		if button == self.transp_btns[4]:
			if mixermode: kn.set_range_color(1)
			globalTransport(92,1,6,15)
			if mixermode: kn.set_range_color()
			self.flash_rec = 1
			


	def pause(self,pause=None):
	#	Triggers random SMR-lights as a pause-effect
		cc = MIDI_CONTROLCHANGE
		smr_chan = config.MIDIChannel - 1
		lights = self.smr_btns[:]
		
		def reset():
			for l in lights: midiOutMsg(cc,smr_chan,l,0)
		
		def rand_val(x):
			random=int(time()*1000)
			random %= x
			return random
		
		def pause_mode():
			p_lights = lights[:]
			reset()
			for l in range(12):
				nr = rand_val(len(p_lights))
				midiOutMsg(cc,smr_chan,p_lights[nr],127)
				p_lights.pop(nr)
		
		if pause == 1:
			if config.Debug:
				if time() - kn.active[0] < (config.SleepTimer * 60) + 2: print("Pause mode active")
			pause_mode()
			self.active[2] = time()
			return
		elif pause == 2:
			if config.Debug: print("Pause mode deactivated")
			reset()
			return


	def get_modes(self,current):
	#	Returns an array with the modes that are enabled in the config.
	#	It's also used to set the default mode at startup.
		modes = []
		if config.MixerMode: modes.append(0)
		if config.ChannelrackMode: modes.append(1)
		if config.PlaylistMode: modes.append(2)
		if config.ControllerLinkMode: modes.append(3)
		if current:
			if len(modes) > 0: return modes[0]
			else: return None
		return modes


	def smr_press(self,event):
		if event.data2 == 127: midiOutMsg(event.midiId,event.midiChan,event.data1,127)
		elif event.data2 == 0: midiOutMsg(event.midiId,event.midiChan,event.data1,0)


def CheckConfig(config):
	# Adds an extra layer of error-detection for the configfile to avoid more complicated
	# errors which the user might not understand.

	boolparams = ['PeakMeter','ReversePeak','BigMeter','Clipping','PlayingOnly','ArmedTracks','ExclusiveSelect','TrackRangeOnly','StickyMaster',
	'ColoredRange','BracketedRange','SelectedPeak','MixerMode','ChannelrackMode','PlaylistMode','ControllerLinkMode']
	numparams = {'MIDIChannel': (1,16), 'TransportChan': (1,16),'SleepTimer': (0,300),'HighlightColor': (-15461356,-1),'TempoBase':(10,397)}

	if not hasattr(config,'Debug'): config.Debug = False

	for p in boolparams + [*numparams]:		# Check for missing parameters
		if not hasattr(config,p) and p == 'ControllerLinkMode': raise RuntimeError("Parameter '"+ p +"' is missing from the config file! Try updating config.py to the latest version.")
		elif not hasattr(config,p): raise RuntimeError("Parameter '"+ p +"' is missing from the config file!")

	for p in numparams:		# Check if number-parameters have the correct type/values
		value = getattr(config,p)
		if type(value) is not int: raise TypeError(p +": Value is of wrong type (must be a number!)")
		elif value not in range(numparams[p][0],numparams[p][1]+1): raise ValueError(p + ": requires a number between " + str(numparams[p][0]) + " and " + str(numparams[p][1]))

	for p in boolparams:		# Check if boolean parameters are set correctly
		value = getattr(config,p)
		if type(value) is not bool: raise TypeError(p +": Value is of wrong type (must be True or False!)")

CheckConfig(config)
