#!/usr/bin/env python3

from bs4 import BeautifulSoup, element
import logging
import requests
from sys import exit

CATEGORY_URL = "https://www.novelleleggere.com/category/"
USER_AGENT = {"User-agent": "Mozilla/5.0"}
TMP_PATH = "tmp/"
TIMEOUT = 5


def get_chapter(url: str) -> (BeautifulSoup, element.Tag):
    logging.info("Downloading and cleaning %s", url)
    try:
        page = requests.get(url, headers=USER_AGENT, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        logging.exception("Connection Error")

    soup = BeautifulSoup(page.text, "html.parser")
    content = soup.find("div", class_="post-content")

    # delete all internal divs
    for s in content.findAll("div"):
        s.extract()

    return soup, content


def get_chapters(name: str, path: str) -> None:
    from math import log10
    from time import sleep

    url = CATEGORY_URL + name.replace(" ", "-").lower()

    logging.info("Getting chapters list of %s, url: %s", name, url)

    try:
        page = requests.get(url, headers=USER_AGENT, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        logging.exception("Connection Error")

    if page.status_code != requests.codes.ok:
        logging.error(page.text)
        exit(1)

    # get chapters list
    soup = BeautifulSoup(page.text, "html.parser")
    chapters_list = soup.find(class_="display-posts-listing")
    raw_chapters = chapters_list.findAll("a")

    # download and clean all chapters
    logging.info("Getting %d chapters", len(raw_chapters))

    n = int(log10(len(raw_chapters))) + 1   # number of digits of the string length
    count = 0

    for elem in raw_chapters[:2]:
        title = elem.string
        url = elem.get("href")

        if (
            title.lower().find("spoiler") != -1
            or title.lower().find("non editato") != -1
        ):
            continue

        soup, chapter = get_chapter(url)

        # remove div class
        del chapter["class"]

        logging.debug("Writing html file for %s", title)

        with open(
            # {path}{count:0>{n}}_{title}.html
            "{}{:0>{}}_{}.html".format(path, count, n, title),
            "w",
        ) as f:
            f.write(str(chapter))

        count += 1
        sleep(2)  # rate limit


def build_epub(name: str, path: str) -> None:
    from os import listdir
    from os.path import isfile, join
    import pypub

    logging.info("Building Epub")

    epub = pypub.Epub(name)

    for f in listdir(path):
        p = join(path, f)
        if isfile(p):
            chapter = pypub.create_chapter_from_file(p, f.replace(".html", ""))
            epub.add_chapter(chapter)

    epub.create(name.lower().replace(" ", "-") + ".epub")


if __name__ == "__main__":
    import argparse
    from os import remove, mkdir, rmdir, listdir

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-q",
            "--quiet",
            dest="loglevel",
            action="store_const",
            const="error",
            default="info",
            help='set logging level to "error"',
        )
        parser.add_argument(
            "-v",
            "--verbose",
            dest="loglevel",
            action="store_const",
            const="debug",
            default="info",
            help='set logging level to "debug"',
        )
        parser.add_argument(
            "-p",
            "--path",
            dest="path",
            action="store",
            nargs=1,
            default=TMP_PATH,
            metavar="path/to/dir",
            help="path where to store temporary files",
        )
        parser.add_argument(
            "name",
            action="store",
            nargs="+",
            metavar="name of series",
            help="name of the series on novelleleggere",
        )
        args = parser.parse_args()

        # setting logging
        logging.basicConfig(
            format="%(asctime)s %(process)d %(levelname)s: %(message)s",
            datefmt="%d/%m/%Y %X",
            level=getattr(logging, args.loglevel.upper()),
        )

        logging.debug("args: %s", args)

        path = args.path
        name = args.name if isinstance(args.name, str) else " ".join(args.name)

        # create cache dir
        mkdir(path)

        get_chapters(name, path)

        build_epub(name, path)

        for f in listdir(path):
            remove(path + f)
        rmdir(path)

    except KeyboardInterrupt:
        exit("\nKeyboard Interrupt received, exiting.")

# vim: ff=unix ts=4 sw=4 stal=2 et sta ai si ft=python
