``` bash
pip3 install -r requirements.txt
head -c 65536 /dev/urandom | python3 -m stuffbuf png output.png [color]
head -c 65536 /dev/urandom | python3 -m stuffbuf wav output.wav
```
