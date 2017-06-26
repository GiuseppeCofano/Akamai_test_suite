#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os, sys
from time import time, sleep
from twisted.internet import reactor
os.environ['PATH'] = '/usr/lib/chromium/:'+os.environ.get('PATH')
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = 'http://wwwns.akamai.com/hdnetwork/demo/flash/default.html'

class Browser:
    def __init__(self, url, duration=10):
        print self, 'start'
        t = time()
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1920, 1080)
        self.driver.set_window_position(-1920, 0)
        self.driver.get(url)
        print self, 'page loaded in %.2f s' %(time()-t)
        sleep(10)
        el = self.driver.find_element_by_id("playerdiv")
        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.move_to_element_with_offset(el, 270, 543)
        action.click()
        action.perform()
        #action.move_to_element_with_offset(el, 5, 5)
        reactor.callLater(duration, self.stop)

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

if __name__ == '__main__':
    for i in xrange(1):
        Browser(URL, 600)
    reactor.run()
