import logging
from sys import stdin, stdout, argv

from stuffbuf.writer.Pipeline import Pipeline


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.INFO)
    pipeline = Pipeline(argv[1])

    if len(argv) > 2:
        outf = open(argv[2], 'wb')
    else:
        outf = stdout.buffer

    if pipeline.source:
        inf = None
    else:
        inf = stdin.buffer

    pipeline.write(inf, outf)
