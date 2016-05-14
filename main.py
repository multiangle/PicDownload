__author__ = 'multiangle'

from PicDownload.aitaotu import aitaotuDownloader

def download(url):
    if 'aitaotu.com' in url:
        ad = aitaotuDownloader()
        ad.download(url)

if __name__=='__main__':
    url = 'http://www.aitaotu.com/weimei/19367.html'
    download(url)
