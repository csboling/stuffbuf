python3 -m stuffbuf 'zx bytedepth=2 exp=2*cos(2*pi*100/44100)*z**-1-z**-2 memdepth=2 init=["sin(0)","sin(2*pi*100/44100)"] | wav' > output.wav
