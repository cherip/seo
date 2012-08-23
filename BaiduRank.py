# -*-coding:utf-8 -*-
#! /bin/bash

# BaiduRank.py

import urllib
import HTMLParser
import re
import sqliteconn

class FindUrlParser(HTMLParser.HTMLParser):
    ''' '''
    def __init__(self, url):
        HTMLParser.HTMLParser.__init__(self)
        self.rank = 0
        self.rank_url = ''
        self.url = url

    def handle_starttag(self, tag, attrs):
        ret_tmp = 0
        if 'table' == tag:
            for key, value in attrs:
                if key == 'id':
                    try:
                        self.ret_tmp = int(value)
                        if self.ret_tmp > 100:
                            self.ret_tmp = 0
                    except:
                        self.ret_tmp = 0
                if key == 'mu':
                    if value.find(self.url) != -1:
                        self.rank = self.ret_tmp
                        self.rank_url = value

def FindSection(html_src, start_tag, end_tag):
    idx = 0
    ret = []
    while True:
        s_tab = html_src.find(start_tag, idx)
        if (s_tab == -1):
            break
        e_tab = html_src.find(end_tag, s_tab)
        #e_tab += len(end_tag)
        s_tab += len(start_tag) + 1
        #print html_src[s_tab:e_tab]
        ret.append(html_src[s_tab:e_tab])
        idx = e_tab
    return ret
                        
def GetFixLink(html_src):
    #print html_src
    #tables = re.findall('<tableclass=>', html_src)
    idx = 0
    ret = []
    table_section = FindSection(html_src, '<table', '</table>')
    right_rank = FindSection(table_section[0], '<font size="-1" color="#008000"', '</font>')
    left_rank = []
    for item in table_section[1:]:
        font = FindSection(item, '<font size=-1 color="#008000"', '</font>')
        left_rank.extend(font)
    left_rank.extend(right_rank)
    #for i in left_rank:
    #    print i
    return left_rank

def find_table(html_src, start):
    s = html_src.find('<table', start)
    if s == -1:
        return -1, ''
    e = html_src.find('>', s)

    #print s, e
    #print html_src[s:e+1]
    return e+1, html_src[s:e+1]

def GetBaiduPageNum(html_src):
    num = FindSection(html_src, '<span class="nums"', '</span>')
    print num 
    if len(num) != 1:
        return ''
    ret = num[0].split(u'约')[1].split(u'个')
    print ret[0]
    return ret

def GetBaiduNum(key):
    html_src = GetBaiduPage(key)
    GetBaiduPageNum(html_src)

def GetBaiduNatureRank(html_src, target_url):
    idx = 0
    htmlparser = FindUrlParser(target_url)
    while True:
        idx, content = find_table(html_src, idx)
        if idx == -1:
            break
        htmlparser.feed(content)
        if htmlparser.rank != 0:
            return htmlparser.rank, htmlparser.rank_url
    return 0,''

def GetBaiduPage(key, page_num=0):
    ''' '''
    attrs = {'ie':'utf-8', 'pn':'0'}
    attrs['pn'] = str(page_num * 10)
    url_attrs = urllib.urlencode(attrs)
    url_domain = 'http://www.baidu.com/s?'
    url = url_domain + url_attrs + '&wd='
    url += key.encode('utf-8')
    print 'try load', url.decode('utf-8').encode('gbk')

    html_src = urllib.urlopen(url).read().decode('utf-8')

    return html_src
    #return GetBaiduNatureRank(html_src, target_url)

def GetBaiduPageFull(key, target_url):
    #print key.encode('gb2312')
    
    #search_key = key.decode('utf-8')
    search_key = key
    for i in xrange(0, 10):
        html = GetBaiduPage(search_key, i)
        rank, rank_url = GetBaiduNatureRank(html, target_url)
        if rank != 0:
            return str(rank), rank_url
            #return rank
    return '0',''

def GetBaiduFixRank(key, target_url):
    #search_key = key.decode('utf-8')
    search_key = key
    html = GetBaiduPage(search_key)
    link = GetFixLink(html)
    for i in xrange(0, len(link)):
        if link[i].find(target_url) != -1:
            return str(i), link[i].split(' ')[0]
    return '0',''

def get_rank_of_group(group):
    keywords = group[2].split('#')
    for key in keywords:
            #print key
            #key.decode('gbk')
        ret = [str(group[0]), key]
        if group[5] == 1:
            my_rank, my_rank_url = GetBaiduPageFull(key, group[3])
            other_rank, other_rank_url = GetBaiduPageFull(key, group[4])
            ret.append(my_rank + '--' + other_rank)
            ret.append(my_rank_url + '--' + other_rank_url)
            ret.append('')
            ret.append('')
        elif group[5] == 2:
            ret.append('')
            ret.append('')
            my_rank, my_rank_url = GetBaiduFixRank(key, group[3])
            other_rank, other_rank_url = GetBaiduFixRank(key, group[4])
            ret.append(my_rank + '|' + other_rank)
            ret.append(my_rank_url + '|' + other_rank_url)
        ret.append('unknown flow')
        print ret
        sqliteconn.insert_multi(ret, 'rank_compare')
   
def get_query_of_group(group):
    keywords = group[3].split('#')
    for key in keywords:
        ret = [str(group[0]), key]
        rank, rank_url = GetBaiduFixRank(key, group[2])
        print rank, rank_url
        rank_type = ''
        if rank != '0':
            ret.append(rank_url)
            rank_type = '1'
        else:
            rank, rank_url = GetBaiduPageFull(key, group[2])
            if rank != '0':
                ret.append(rank_url)
                rank_type = '2'
            else:
                ret.append('failed found!')
                rank_type = '0'
        ret.append('unknown')
        ret.append('unknown')
        ret.append('unknown')
        ret.append(rank_type)    

        sqliteconn.insert_multi(ret, 'key_query')

def thread_rank():
    group_ret = sqliteconn.read_group_info('group_info_rank')
    for group in group_ret:
        get_rank_of_group(group)

def thread_query():
    group_ret = sqliteconn.read_group_info('group_info_query')
    for group in group_ret:
        get_query_of_group(group)   

if __name__ == '__main__':
    #src = open('1.txt').read()

    #print GetBaiduPageFull('鲜花', 'bj.58.com')
    #print GetBaiduFixRank('鲜花', 'zhenaihuawu.com')
    #thread_rank()
    #thread_query()
    GetBaiduNum(u'鲜花')