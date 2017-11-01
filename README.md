# nettomidi

Uses scapy and python-rtmidi to interpret network traffic as MIDI.

### Prerequisites

* Python 2.7
* wpcap driver (wireshark)
* loopMIDI https://www.tobias-erichsen.de/software/loopmidi.html (windows only)

### Installing

Setup nettomidi:
```
git clone git@github.com:RyanJarv/nettomidi.git
cd nettomidi
virtualenv .
. ./bin/activate
pip install -r requirements.txt

```

Add midi loop back with loopMIDI

Run:
```
python2 ./nettomidi.py
```

If you are running Ableton you should start recieving MIDI events now.
