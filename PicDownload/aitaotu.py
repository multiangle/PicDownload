__author__ = 'multiangle'


import urllib.request as request
from .Basic import BasicDownloader, AsyBasicDownloader
from bs4 import BeautifulSoup
import re
import json

class aitaotuDownloader(AsyBasicDownloader):
    def __init__(self):
        BasicDownloader.__init__(self)
        self.basic_url = 'https://www.aitaotu.com/'
        self.encoding = 'utf8'
    #Override
    def parsePage(self,page_str):
        if isinstance(page_str,str):
            page = BeautifulSoup(page_str,'lxml')
        elif isinstance(page_str,BeautifulSoup):
            page = page_str
        else:
            return None

        try:
            return self.__parse_1(page)
        except:
            try:
                return self.__parse_2(page)
            except:
                return self.__parse_3(page)

    def __parse_1(self,page):

        ret_data = {}
        div_photo = page.find('div',attrs={'class':'photo'})

        # get pic url (important)
        div_bigpic = div_photo.find('div',attrs={'class':'big-pic'})
        img_list = div_bigpic.find_all('img')
        img_url_list = [x['src'] for x in img_list]
        ret_data['img_url_list'] = img_url_list

        # get page num (important)
        div_pages = page.find('div',attrs={'class':'pages'})
        div_pages_li = div_pages.find_all('li')
        last_url = div_pages_li[-1]
        page_num = re.findall(re.compile(r'_\d+.html'),str(last_url))[0][1:-5]
        ret_data['page_num'] = int(page_num)

        # get current page
        li_this = page.find('li',attrs={'class':'thisclass'})
        ret_data['current_page'] = int(li_this.text)

        # get titles
        title = div_photo.find('div',attrs={'class':'sut6552','id':'photos'}).find('h1').text
        ret_data['title'] = title

        return ret_data

    def __parse_2(self,page):

        ret_data = {}
        div_photo = page.find('div',attrs={'class':'photo'})

        # get pic url (important)
        div_bigpic = div_photo.find('div',attrs={'class':'big-pic'})
        img_list = div_bigpic.find_all('img')
        img_url_list = [x['src'] for x in img_list]
        ret_data['img_url_list'] = img_url_list

        return ret_data

    def __parse_3(self,page): # 移动端
        ret_data = {}

        # img url
        div_arcmain = page.find_all('div',attrs={'class':'arcmain'})[1]
        img_list = div_arcmain.find_all('img')
        img_url_list = [x['src'] for x in img_list]
        for i in range(img_url_list.__len__()):
            img_url_list[i] = img_url_list[i].replace('wap','')
            img_url_list[i] = img_url_list[i].replace(':8090',':8089')
        ret_data['img_url_list'] = img_url_list

        div_articlepage = page.find('div',attrs={'class':'article-page'})
        page_info = div_articlepage.find('li').text
        page_info = page_info.split('/')
        ret_data['page_num'] = int(page_info[1])
        ret_data['current_page'] = int(page_info[0])
        return ret_data
    #Override
    def build_url(self,input_url,page_id):
        ret_str = input_url[:-5] + '_'+str(page_id) + '.html'
        # print(ret_str)
        return ret_str
