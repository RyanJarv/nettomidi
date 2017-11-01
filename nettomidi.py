#!/usr/bin/env python
from __future__ import print_function

from scapy.all import *
import time
import sys

import rtmidi

# Works around windows issue
# https://stackoverflow.com/questions/40793615/scapy-windows-sniff-log-runtime-is-not-defined
from scapy.arch.windows import compatibility
from scapy.all import log_runtime, MTU, ETH_P_ALL, PcapTimeoutElapsed, plist

compatibility.log_runtime = log_runtime
compatibility.MTU = MTU
compatibility.PcapTimeoutElapsed = PcapTimeoutElapsed
compatibility.ETH_P_ALL = ETH_P_ALL
compatibility.plist = plist


class Track:
    root = 48
    octaves = 4
    scale = []
    scale=[0, 2, 4, 5, 7, 9, 11]
    min_duration = 0.2
    max_duration = 1.0
    min_volume = 0
    max_volume = 100
    fade = 200000
    filter = ""
    notes = []

    tcp_start_seq = {}

    def __init__(self):
        for octave in range(1, self.octaves + 1):
            self.notes += map(lambda x: x * octave + self.root, self.scale)

    def start(self):
        sniff(filter=self.filter, prn=track.packet_note)

    def packet_note(self, p):
        note = IPNote(track)

        note.ip_source(p[IP].src)
        note.ip_length(int(p.sprintf('%IP.len%')))

        try:
            p[TCP]
            seq = long(p.sprintf('%TCP.seq%'))
            if (note.src_ip not in self.tcp_start_seq) or (seq < self.tcp_start_seq[note.src_ip]):
                self.tcp_start_seq[note.src_ip] = seq
            note.seq(seq - self.tcp_start_seq[note.src_ip])
            print(seq - self.tcp_start_seq[note.src_ip])
        except IndexError:
            print('.')
            note.volume = self.max_volume + self.min_volume / 2

        note.play()

class IPNote:
    volume = 0
    pitch = 0
    duration = 0
    src_ip = ''

    def __init__(self, track):
        self.track = track

    def ip_length(self, length):
        self.duration = (length / 1500) * (self.track.max_duration - self.track.min_duration) + self.track.min_duration

    def ip_source(self, ip):
        self.src_ip = ip
        self.pitch = int(ip.replace('.', ''))
        self.pitch = self.track.notes[self.pitch % len(self.track.notes)]

    def seq(self, seq):
        self.volume = max((self.track.fade - seq)/float(self.track.fade), 0) * (self.track.max_volume - self.track.min_volume) + self.track.min_volume

    def play(self):
        self.send_on()
        time.sleep(self.duration)
        self.send_off()

    def send_on(self):
        midiout.send_message([0x90, self.pitch, self.volume])

    def send_off(self):
        midiout.send_message([0x80, self.pitch])

midiout = rtmidi.MidiOut()

if not len(midiout.get_ports()) >= 2:
    print("Only one port found (should be two?)")

midiout.open_port(1)
print(midiout.get_ports())

track = Track()

try:
    track.start()
except KeyboardInterrupt:
    pass
