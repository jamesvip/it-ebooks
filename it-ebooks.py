#! /usr/bin/env python
#! encoding:utf-8
__author__ = "James.Zhang"
import re
import requests
import os
from os.path import getsize,join
import sys
import logging
from bs4 import BeautifulSoup

"""
从www.it-ebooks.info下载，有VPN速度会快
在query处填需要的书类别，注意大小写
在local_dir处填写本地下载路径
"""

print u"下载书籍关键字：", sys.argv[1]
query = sys.argv[1]

local_dir = "E:\\Book\\"+query+"\\"

if not os.path.exists(local_dir):
    os.makedirs(local_dir)

def remote_down_url(remote_url):
    """
    寻找下载书籍链接函数和书籍大小函数
    """

    regex_file_url = r"http://filepi.com/i/(([a-zA-Z]|[0-9])*)"
    #regex_file_url = r"http://filepi.com/i/(\w)"
    down_url_pre = "http://it-ebooks.info/book"
    r = requests.get(remote_url)
    """
    add file size
    """
    soup = BeautifulSoup(r.content)
    justify = soup.find_all("td",{"class":"justify link"})
    global size
    size = justify[0].contents[5].find_all("b")[7].text

    if r.status_code == 200:  #判断网页能否正常访问
        re_file = r.text

        if re.search(regex_file_url,re_file) != None:
            #如果search()的值不为空，即说明能提取到电子书下载地址
            match = re.search(regex_file_url,re_file)
            global down_url
            down_url = str(match.group())
            logging.info("DownUrl %s", down_url)

        else:
            down_url = "error"
            print (".....No Search Down Url.....")
            logging.info(".....No Search Down Url.....")
    else:
        print ("ERROR 404!....")
def validatename(book_name):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
    new_bookname = re.sub(rstr, "", book_name)
    return new_bookname

def down_book(down_url,url,book_name,local_dir):
    """
    下载书籍，下载过程中后缀.tmp,下载完成判断大小，如果满足文件大小70%则认为成功并修改文件后缀
    """
    book_name = validatename(book_name)
    # book_name = book_name.replace("/","")
    down_dir_tmp = str(local_dir) + str(book_name)+ ".pdf"+".tmp"
    down_dir = str(local_dir) + str(book_name)+ ".pdf"
    if os.path.exists(down_dir) == True and abs(round(float(getsize(down_dir))/1024/1024,1) - round(float(size.replace(' MB',"")),1)) < 1: #判断书籍是否被下载过，如已存在文件则跳过
        #sys.exit()

        print ("....<"+book_name+"> already exists...")
        logging.info("....Books already exists....")
    elif os.path.exists(down_dir_tmp) == True or os.path.exists(down_dir) == False:
        if os.path.exists(down_dir_tmp) == True:
            print "...ReDownloading <"+book_name+">..."
            print "Original Size: "+size
            os.remove(down_dir_tmp)
        else:
            print "...Downloading <"+book_name+">..."
            print "Original Size: "+size
        rp = requests.get(down_url,headers = {'Referer':url},allow_redirects = False)
        r = requests.get(rp.headers['location'])
        with open(down_dir_tmp, "wb") as code:
           code.write(r.content)

        print "Actual Size: "+str(round(float(getsize(down_dir_tmp))/1024/1024,1))+" MB"
        if abs(round(float(getsize(down_dir_tmp))/1024/1024,1) 
            - round(float(size.replace(' MB',"")),1))/round(float(size.replace(' MB',"")),1) < 0.3:#此处可调整，如果下载不到原有的70%认为没下载成功
            os.rename(down_dir_tmp,down_dir)




urlinit = "http://it-ebooks.info/search/?q="+query+"&type=title&page="
regex_book_link = r'<a href=\"/book(.*)'

i = 1

"""
如果本页一个符合关键字的书籍都没有(Done=10)，则退出
"""
Done = 0
while Done < 10:
    url=urlinit+str(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    links = soup.find_all("a",href = True)
    for link in links:
        if re.search(regex_book_link,str(link)) != None and link.text != '':
            book_name = link.text
            preurl = 'http://it-ebooks.info'+link['href']
            if query in book_name:
                Done = 0
                remote_down_url(preurl)
                # print down_url
                down_book(down_url,preurl,book_name,local_dir)
            else:
                Done = Done + 1
    i = i + 1
    #print Done


