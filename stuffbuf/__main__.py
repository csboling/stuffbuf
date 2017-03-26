from sys import stdin, stdout, argv

from stuffbuf.writer.Pipeline import Pipeline


if __name__ == '__main__':
    pipeline = Pipeline(argv[1])

    if len(argv) > 2:
        outf = open(argv[2], 'wb')
    else:
        outf = stdout.buffer

    pipeline.write(stdin.buffer, outf)
