__author__ = 'multiangle'

import threading
import urllib.request as request
import time
import os
import re
import config
import asyncio
import aiohttp
import pprint

class BasicDownloader():
    def __init__(self):
        # threading.Thread.__init__(self)
        self.encoding = 'utf8'

    def parsePage(self,page_str):
        """
        @param page, type of beautifulsoup
        @return type of dict
            necessary keys:
                img_url_list
                page_num
            unnecessary keys:
                current_page
                title
        """
        return None

    def build_url(self,input_url,page_id):
        return None

    def download(self,page_url):
        init_page = request.urlopen(page_url,timeout=config.TIMEOUT).read()
        init_page = str(init_page,encoding='utf8')
        thread_info = self.parsePage(init_page)

        if thread_info == None:
            raise EnvironmentError("The method of parsePage should be Overrided")
        info_keys = thread_info.keys()
        if 'img_url_list' not in info_keys or 'page_num' not in info_keys:
            raise ValueError("parsePage cant get enough information")
        if not os.path.exists(config.STORE_FOLDER):
            print("The store file not exists, will create a new one")
            os.makedirs(config.STORE_FOLDER)

        # title
        if 'title' in info_keys :
            title = thread_info['title']
            title = title.replace('\\','')
            title = title.replace('/','-')
            print(title)
        else:
            title = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        # page_num
        page_num = thread_info['page_num']
        # pic_num_perpage
        pic_num_perpage = thread_info['img_url_list'].__len__()

        # 创建帖子文件夹
        content_folder = config.STORE_FOLDER + os.sep + title
        if not os.path.exists(content_folder):
            os.makedirs(content_folder)

        page_list=[dict(type='page',id=i+1,url=self.build_url(page_url,i+1))
                   for i in range(page_num)]
        page_ret_list = []
        pic_url_list = []
        pic_ret_list = []
        page_thread = []
        pic_thread = []
        for i in range(config.PAGE_THREAD):
            page_thread.append(Downloader(page_list,page_ret_list,encoding=self.encoding))
        for i in range(config.PIC_THREAD):
            pic_thread.append(Downloader(pic_url_list,pic_ret_list,encoding=self.encoding))
        for t in page_thread:
            t.start()
        for t in pic_thread:
            t.start()

        page_count = 0
        while True:
            if page_ret_list.__len__()>0:
                task = page_ret_list.pop(0)
                id = task['id']
                page = task['data']
                parse_res = self.parsePage(page)
                img = parse_res['img_url_list']
                print(img)
                for i in range(img.__len__()):
                    pic_url_list.append(dict(
                        type = 'pic',
                        url = img[i],
                        id = (id-1) * pic_num_perpage + i + 1
                    ))
                page_count += 1
                if page_count>=page_num :
                    page_list += [dict(type='end')]*config.PAGE_THREAD*config.ASY_BATCH_SIZE
                    pic_url_list += [dict(type='end')]*config.PIC_THREAD*config.ASY_BATCH_SIZE

            if pic_ret_list.__len__()>0:
                task = pic_ret_list.pop(0)
                id = task['id']
                pic = task['data']
                url = task['url']
                form = re.findall(re.compile(r'\.[\w]+'),url)[-1]
                file_path = content_folder + os.sep + str(id) + form
                f = open(file_path,'wb')
                f.write(pic)
                f.close()

            all_stop = True
            for t in pic_thread:
                if t.is_alive():
                    all_stop = False
            if all_stop:
                break

class Downloader(threading.Thread):
    def __init__(self,task_list,ret_list,encoding='utf8'):
        threading.Thread.__init__(self)
        self.task_list = task_list
        self.ret_list = ret_list
        self.encoding = encoding

    def run(self):
        while True :
            if self.task_list.__len__()>0:
                task = self.task_list.pop(0)
            else:
                continue

            if task['type']=='end':
                break
            elif task['type']=='page':
                # 需要task项有 type,id,url , 返回值有id,type,data几项
                url = task['url']
                try:
                    data = self.getData(url,encoding=self.encoding)
                    ret = dict(
                        id = task['id'],
                        type = 'page',
                        data = data,
                        url = url
                    )
                    self.ret_list.append(ret)
                except:
                    self.task_list.insert(0,task)
            elif task['type']=='pic':
                url = task['url']
                print(url)
                id = task['id']
                try:
                    pic = self.getData(url,encoding=False)
                    ret = dict(
                        id = id,
                        type = 'pic',
                        data = pic,
                        url = url
                    )
                    self.ret_list.append(ret)
                except:
                    self.task_list.insert(0,task)
            else:
                raise ValueError('Unknown task type')

    def getData(self,url,encoding='utf8'):
        try:
            res=self.getData_inner(url,encoding)
            return res
        except Exception as e:
            reconn_count=1
            while reconn_count<=config.RECONN_NUM:
                # time.sleep(max(random.gauss(2,0.5),0.5))
                try:
                    res=self.getData_inner(url,encoding)
                    return res
                except:
                    reconn_count+=1
            raise ConnectionError('Unable to get page')

    def getData_inner(self,url,encoding='utf8'):
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) '
                                 'AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile'
                                 '/12A4345d Safari/600.1.4'}
        req=request.Request(url)
        opener=request.build_opener()
        request.install_opener(opener)
        result=opener.open(req,timeout=config.TIMEOUT)
        if encoding:
            return result.read().decode(encoding=encoding)
        else:
            return result.read()

class AsyBasicDownloader():
    def __init__(self):
        self.encoding = 'utf8'

    def parsePage(self,page_str):
        """
        @param page, type of beautifulsoup
        @return type of dict
            necessary keys:
                img_url_list
                page_num
            unnecessary keys:
                current_page
                title
        """
        return None

    def build_url(self,input_url,page_id):
        return None

    def download(self,page_url):
        init_page = request.urlopen(page_url,timeout=config.TIMEOUT).read()
        init_page = str(init_page,encoding='utf8')
        thread_info = self.parsePage(init_page)
        print(thread_info)
        if thread_info == None:
            raise EnvironmentError("The method of parsePage should be Overrided")
        info_keys = thread_info.keys()
        if 'img_url_list' not in info_keys or 'page_num' not in info_keys:
            raise ValueError("parsePage cant get enough information")
        if not os.path.exists(config.STORE_FOLDER):
            print("The store file not exists, will create a new one")
            os.makedirs(config.STORE_FOLDER)

        # title
        if 'title' in info_keys :
            title = thread_info['title']
            title = title.replace('\\','')
            title = title.replace('/','-')
            print(title)
        else:
            title = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        # page_num
        page_num = thread_info['page_num']
        # pic_num_perpage
        pic_num_perpage = thread_info['img_url_list'].__len__()

        # 创建帖子文件夹
        content_folder = config.STORE_FOLDER + os.sep + title
        if not os.path.exists(content_folder):
            os.makedirs(content_folder)

        page_list=[dict(type='page',id=i+1,url=self.build_url(page_url,i+1))
                   for i in range(page_num)]
        page_ret_list = []
        loop = asyncio.get_event_loop()
        tasks = [self.getPage(task,page_ret_list) for task in page_list]
        loop.run_until_complete(asyncio.wait(tasks))
        # print(page_ret_list)

        page_infos = [x['data'] for x in page_ret_list]
        img_urls = [self.parsePage(page)['img_url_list'] for page in page_infos]
        img_urls = sum(img_urls,[])
        img_urls = sorted(img_urls)
        img_ret = []
        img_tasks = [dict(url=img_urls[i],id=i) for i in range(img_urls.__len__())]
        img_tasks = [self.getPage(x,img_ret,encoding=None) for x in img_tasks]
        loop.run_until_complete(asyncio.wait(img_tasks))
        # loop.close()
        img_ret = sorted(img_ret,key=lambda x:x['task']['url'])
        count = 0
        for img in img_ret:
            count += 1
            pic = img['data']
            id = count
            url = img['task']['url']
            form = re.findall(re.compile(r'\.[\w]+'),url)[-1]
            file_path = content_folder + os.sep + str(id) + form
            f = open(file_path,'wb')
            f.write(pic)
            f.close()
        print('done')

    @asyncio.coroutine
    async def getPage(self,task,ret_list,encoding='utf8'):
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) '
                                 'AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile'
                                 '/12A4345d Safari/600.1.4'}
        url = task['url']
        async with aiohttp.ClientSession() as session:
                async with session.get(url,headers=headers) as resp:
                    content = await resp.read()
                    if encoding:
                        content = content.decode(encoding)
                    ret_list.append(dict(
                        data = content,
                        task = task
                    ))
                    print(url+'\t'+'done')

class AsyDownloader(threading.Thread):
    def __init__(self,task_list,ret_list,batch_size=config.ASY_BATCH_SIZE,encoding='utf8'):
        threading.Thread.__init__(self)
        self.task_list = task_list
        self.ret_list = ret_list
        self.encoding = encoding
        self.batch_size = batch_size

    def run(self):
        while True:
            task_batch = []
            for i in range(self.batch_size):
                if self.task_list.__len__() == 0:
                    break
                task1 = self.task_list.pop(0)
                if task1['type'] == 'end':
                    break
                task_batch.append(task1)
            if task_batch.__len__() == 0:
                break

            # 异步模块，进行任务的打包和异步执行
            loop = asyncio.get_event_loop()
            batch_ret = []
            batch_tasks = [self.getPage(task,batch_ret) for task in task_batch]
            loop.run_until_complete(batch_tasks)
            loop.close()
            for res in batch_ret:
                data = res['data']
                task = res['task']

                ret = dict(
                    id = task['id'],
                    data = data,
                    url = task['url']
                )
                if task == 'page':
                    ret['type'] = 'page'
                elif task == 'pic':
                    ret['type'] = 'pic'
                else:
                    raise ValueError('Unknown task type')

    @asyncio.coroutine
    async def getPage(self,task,ret_list,encoding='utf8'):
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) '
                                 'AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile'
                                 '/12A4345d Safari/600.1.4'}
        url = task['url']
        # with aiohttp.Timeout(5):
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as resp:
                    content = await resp.read()
                    if encoding:
                        content = content.decode(encoding)
                    ret_list.append(dict(
                        data = content,
                        task = task
                    ))



















