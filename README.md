``` bash
pip3 install -r requirements.txt
head -c 65536 /dev/urandom > input
cat input | python3 -m stuffbuf png output.png
cat input | python3 -m stuffbuf wav output.wav
```

Some converters take options:

``` bash
cat input | python3 -m stuffbuf 'png color' output.png
```

Some converters are sources and do not require an input file if they
are at the beginning of a pipeline:

``` bash
python3 -m stuffbuf 'lfsr taps=0x123456 | png color' output.png
```

You can also sequence conversions together:

``` bash
cat input | python3 -m stuffbuf 'png | wav | png color'
```

Stuffbuf as a Service:

``` bash
docker-compose up -d
HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' stuffbuf)
cat input | nc $HOST 51966
```
