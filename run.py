# -*-coding:utf-8 -*-

import threading
import time
import BaiduRank
import GetCompany
import PrBdkey

class thread_company(threading.Thread):
    ''''''
    def __init__(self, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_company')
        self.interval = interval

    def run(self):
        while True:
            GetCompany.thread_crawler_company()
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

class thread_word_sug(threading.Thread):
    ''''''
    def __init__(self, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_sug')
        self.interval = interval

    def run(self):
        while True:
            PrBdkey.thread_sug()
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

class thread_rank(threading.Thread):
    ''''''
    def __init__(self, interval=60*1):
        threading.Thread.__init__(self, name = 'crawler_rank')
        self.interval = interval

    def run(self):
        while True:
            BaiduRank.thread_rank()
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'


class thread_query(threading.Thread):
    ''''''
    def __init__(self, interval=60*1):
        threading.Thread.__init__(self, name = 'crawler_query')
        self.interval = interval

    def run(self):
        while True:
            BaiduRank.thread_query()
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

def main():
    crawler_company = thread_company()
    crawler_query = thread_query()
    crawler_rank = thread_rank()
    crawler_sug = thread_word_sug()
    
    crawler_company.start()    
    crawler_query.start()
    crawler_rank.start()
    crawler_sug.start()

    crawler_query.join()
    crawler_rank.join()
    crawler_company.join()
    crawler_sug.join()

if __name__ == '__main__':
    main()