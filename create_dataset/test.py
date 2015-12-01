#!/usr/bin/python

import easyprogressbar


def main():
    pb = easyprogressbar.EasyProgressBar()
    pb.start()
    for i in range(100):
        print i
        pb.update(i)
    pb.finish()


if __name__ == "__main__":
    main()
