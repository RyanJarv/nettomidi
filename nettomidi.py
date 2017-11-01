#!/usr/bin/env python
from scapy.all import *
from midiutil import MIDIFile
import time

root  = 48
octaves  =  4

scale    = [0, 2, 4, 5, 7, 9, 11]

NOTES = []
for octave in range(1, octaves + 1):
    NOTES += map(lambda x: x * octave + root, scale)

track    = 0
channel  = 0
start    = time.time()
tempo    = 600  # In BPM

min_duration = 1   # In beats
max_duration = 30   # In beats

min_volume   = 0 # 0-127, as per the MIDI standard
max_volume   = 100

tcp_start_seq = {}
fade = 2000

def addnote(p):
    global start, NOTES
    beat = int((time.time() - start) * tempo/60)

    try:
        src = p[IP].src
    except IndexError:
        return

    pitch = int(src.replace('.', ''))
    pitch = NOTES[pitch % len(NOTES)]

    duration = (int(p.sprintf('%IP.len%')) / 1500) * (max_duration - min_duration) + min_duration

    try:
        seq = int(p.sprintf('%TCP.seq%'))
        if (src not in tcp_start_seq) or (seq < tcp_start_seq[src]):
            tcp_start_seq[src] = seq
        seq = seq - tcp_start_seq[src]
        volume = max((fade - seq)/float(fade), 0) * (max_volume - min_volume) + min_volume
    # May not be TCP
    except ValueError:
        volume = max_volume + min_volume / 2

    MyMIDI.addNote(track, channel, pitch, beat, duration, int(volume))

MyMIDI = MIDIFile(1) # One track, defaults to format 1 (tempo track
                     # automatically created)
MyMIDI.addTempo(track, 0, tempo)

try:
    sniff(prn=addnote)
except KeyboardInterrupt:
    pass

with open("major-scale.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
