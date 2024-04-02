#!/usr/bin/env python3

def get_chapters(name: str):
    import requests
    from bs4 import BeautifulSoup

    # TODO

if __name__ == '__main__':
    from sys import exit
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target",
                        metavar="\"path/to/dir\"", default="",
                        help="path to target directory")
    args = parser.parse_args()

    # TODO

    exit(0)

# vim: sw=4
