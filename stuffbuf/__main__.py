from sys import stdin, stdout, argv

import stuffbuf.writer as writer


if __name__ == '__main__':
    w = writer.Writer.create(argv[1])
    if len(argv) > 2:
        f = open(argv[2], 'wb')
    else:
        f = stdout.buffer
    w.write(stdin.buffer, f, *argv[3:])
