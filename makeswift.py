# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Name:        The-Swift-Programming-Language
# Purpose:     Web crawler of Swift, Python is slow-------
#
# Author:      muxuezi@gmail.com
#
# Created:     06/06/2014
# Copyright:   (c) muxuezi 2014
# Licence:     <All licence>
#-------------------------------------------------------------------------
from bs4 import BeautifulSoup
import requests
import re
import time
import thread


allPageCnt = {}
mutex = thread.allocate_lock()
exitmutexes = [thread.allocate_lock() for i in range(38)]
baseUrl = 'https://developer.apple.com/library/prerelease/ios/documentation/Swift/Conceptual/Swift_Programming_Language/'


def cleanpage(url):
    soup = BeautifulSoup(requests.get(url).content, "lxml")
    h2 = soup.find('ul', class_="list-bullet")
    artHtml = str(soup.find('article', class_="chapter"))
    styleChange = [('<ul', '<ol'), ('</ul>', '</ol>'), ('<h2', '<h1'), ('href=".+?#', 'href="#')]
    artHtml = re.sub(re.compile('<section\sclass=""\sid="next_previous">.+?</section>', re.DOTALL), '', artHtml)
    artHtml = re.sub(re.compile('<div\sid="mini_toc_button">+?</div>', re.DOTALL), '', artHtml)
    for x, y in styleChange:
        artHtml = re.sub(re.compile(x), y, artHtml)
    fmt1 = lambda x: '<h3 class="section-name" tabindex="0">%s</h3>' % x
    fmt2 = lambda x: '<h2 class="section-name" tabindex="0">%s</h2>' % x
    try:
        h2All = map(lambda x: x.text.strip(), h2.findAll('a'))
    except AttributeError:
        pass
    else:
        for x in h2All:
            x = str(x)
            artHtml = artHtml.replace(fmt1(x), fmt2(x))
    return artHtml


def getpage(idx, unit, mutex):
    # web crawler
    with mutex:
        url, name = unit
        url = baseUrl + url
        page = cleanpage(url)
        allPageCnt[idx + 1] = page
        print idx + 1, name
    exitmutexes[idx].acquire()


def main():
    # read all links
    soup = BeautifulSoup(requests.get(baseUrl).content, "lxml")
    pageLable = soup.find('nav', class_="book-parts hideInXcode")
    allLink = map(lambda x: (x.get('href'), x.text), pageLable.findAll('a'))
    for idx, unit in enumerate(allLink):
        thread.start_new_thread(getpage, (idx, unit, mutex))
    while True:
        if all(mutex.locked() for mutex in exitmutexes):
            with open('swift.html', 'wb') as f:
                styleChange = [('<ul', '<ol'), ('</ul>', '</ol>'), ('<h2', '<h1'), ('href=".+?#', 'href="#')]
                pageLable = str(pageLable)
                for x, y in styleChange:
                    pageLable = re.sub(re.compile(x), y, pageLable)
                f.write(pageLable+'\n') # writes page titles
                for k, apage in sorted(allPageCnt.items()):
                    f.write(apage)
            print 'All done'
            break
        else:
            time.sleep(0.01)

if __name__ == '__main__':
    main()
