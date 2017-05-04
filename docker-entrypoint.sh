#! /bin/sh

while true
do
    nc -lk -p ${PORT} -e /src/entrypoint.sh
done
