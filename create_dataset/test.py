#!/usr/bin/python

import easyprogressbar


def tt():
    a = 1
    b = 2
    return a, b


def main():
    pb = easyprogressbar.EasyProgressBar()
    pb.start()
    for i in range(100):
        print i
        pb.update(i)
    pb.finish()
    a = tt()
    print a


if __name__ == "__main__":
    main()
