__author__ = 'multiangle'

from PicDownload.aitaotu import aitaotuDownloader
import re

def download(url):
    if 'aitaotu.com' in url:
        ad = aitaotuDownloader()
        ad.download(url)

if __name__=='__main__':
    # url = 'http://www.aitaotu.com/guonei/7941.html'

    # ids=input("id : ")
    # ids = re.sub(' ','',ids) # 去掉空格
    # ids = ids.split('|')
    # ids = [int(x) for x in ids]
    ids = [24036]
    for id in ids:
        url = 'http://www.aitaotu.com/guonei/{id}.html'.format(id=id)
        download(url)
