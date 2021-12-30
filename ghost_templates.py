# -*- coding: utf-8 -*-
from asyncio.tasks import wait
import os
import telnetlib
import requests
from lxml import etree
import aiohttp
import traceback
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

def clear(data):
    d = str(data).replace("[", "").replace("]", "").replace("'", "")
    return d

#获取图片地址
def get_img_url(i):
    for j in range(0,999):
        proxies = get_random_proxies()
        url = f"https://www.ghostoact.com/arts/models/?cp={i}&sk={j}"
        l = []
        res = requests.get(url=url, headers=headers,proxies=proxies)
        if res.status_code == 200:
            html = etree.HTML(res.content.decode())
            img_url = html.xpath(
                "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[2]/a/@href"
            )
            title = html.xpath("/html/body/div[4]/div[2]/div[1]/div[2]/p[1]/a/text()")
            name = html.xpath("/html/body/div[4]/div[2]/div[1]/div[2]/p[2]/a/text()")
            for z in zip(title, name):
                filename = z[1] + " " + z[0]
            l.append(str(img_url))
            l.append(filename)
            img_urls.append(clear(l[len(l) - 2]))
            img_titles.append(l[len(l) - 1])
        elif res.status_code==500:
            continue
        else:
            print('网站请求失败')
            continue
            # get_img_url(i)
# 异步下载图片
async def downld_img(img_url, img_title):
    proxy = get_random_proxy() 
    while proxy == None:
        proxy = get_random_proxy()
    else:
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), trust_env=True) as session:
                async with session.get(img_url,headers=headers,proxy=proxy) as res:
                    if not os.path.exists("img"):
                        os.mkdir("img")
                        print("没有img文件夹，创建img文件夹")
                        with open("./img/" + clear(img_title) + ".jpg", mode="wb") as f:
                            f.write(await res.content.read())
                            print(clear(img_title) + "下载成功!")
                            """
                            async with aiofiles.open("./img/" + clear(name) + ".jpg", mode="wb") as f:
                            await f.write(res.read())
                            await f.close()
                            """
                    else:
                        with open("./img/" + clear(img_title) + ".jpg", mode="wb") as f:
                            f.write(await res.content.read())
                            print(clear(img_title) + "下载成功!")
        except Exception:
            print(img_title,'请求失败,继续下次请求')
            print(traceback.format_exc())
            downld_img(img_url, img_title)
#多线程请求图片地址
def get_url_thread():
    poollist = []
    with ThreadPoolExecutor(10) as pool:
        for i in range(1,999):
            pool.submit(get_img_url,i)
        pool.shutdown()
#异步协程下载图片
async def downld_img_main(img_urls):

    tasks = []
    for img_url, img_title in zip(img_urls, img_titles):
        d = asyncio.create_task(downld_img(img_url, img_title))
        tasks.append(d)
    await asyncio.wait(tasks)

#取消 Event loop is closed 警告
def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper
#请求代理池获取下载图片URL的IP与端口
def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    res = requests.get(proxypool_url)
    ip = res.text.rsplit(':',1)[0]
    port = res.text.rsplit(':',1)[1]
    try:
        #检测IP是否可用
        telnetlib.Telnet(host=ip, port=int(port), timeout=3)
    except:
        print('IP失效,更换可用IP')
        get_random_proxy()
    else:
        print(res.text,'IP可用')
        text =  res.text.strip()
        return 'http://'+text
#请求代理池获取爬取网站的代理IP地址
def get_random_proxies():
    """
    get random proxy from proxypool
    :return: proxy
    """
    res = requests.get(proxypool_url)
    ip = res.text.rsplit(':',1)[0]
    port = res.text.rsplit(':',1)[1]
    try:
        #检测IP是否可用
        telnetlib.Telnet(ip, port=port, timeout=20)
    except:
        print('IP失效,更换可用IP')
        get_random_proxies()
    else:
        print(res.text,'IP可用')
        text =  res.text.strip()
        return {'http':'http://' + text}

if __name__ == "__main__":
    #修改事件循环的策略，不能放在协程函数内部，这条语句要先执行
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #IP代理池的地址
    proxypool_url = 'http://119.23.249.195:5555/random'
    #请求头
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Cookie": "PHPSESSID=cjju7afbeeds4v571528lheh34; UM_distinctid=17e04db391ba7-0c4cdf0db7f207-f7d123e-1fa400-17e04db391cc49; CNZZDATA1259919941=1847624630-1640751975-%7C1640751975",
    "Host": "www.ghostoact.com",
    }
    print("正在请求数据中,请勿关闭...")
    #取消 Event loop is closed 警告
    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
        _ProactorBasePipeTransport.__del__
    )
    #保存英雄名称与图片地址的列表
    img_titles = []
    img_urls = []
    #1、多线程获取图片地址
    get_url_thread()
    print(img_urls)
    #2、异步协程下载英雄皮肤图片
    asyncio.run(downld_img_main(img_urls))
