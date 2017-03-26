from sys import stdin, argv

import stuffbuf.writer as writer


if __name__ == '__main__':
    w = writer.Writer.create(argv[1])
    w.write(stdin.buffer, *argv[2:])
