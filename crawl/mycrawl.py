# encoding: utf-8
import requests
import time
import aiohttp, asyncio
from lxml import etree
from selenium import webdriver

# 请求url
url = 'http://python.jobbole.com/all-posts/'
# 请求头, cookie也可以直接放入
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
# 请求参数
params = {"a": "test"}
# 代理
proxies = {"http": "88.99.149.188:31288", "https": "88.99.149.188:31288"}
# cookie
cookies = {'from-my': 'browser'}

# 发起请求get/post
# resp = requests.get(url=url, headers=headers, params=params, proxies=proxies, cookies=cookies)
# resp = requests.get(url=url, headers=headers)
# 启动firefox
browser = webdriver.Firefox()
# 请求url
browser.get(url)
# 
resp = {"status_code":200, "text":browser.page_source}

# 异步获取图片内容
async def get_content(link):
    async with aiohttp.ClientSession() as session:
        response = await session.get(link)
        content = await response.read()
        return content

# 保存图片
async def download_img(img):
    name = img.split('/')[-1]
    content = await get_content(img)
    with open(name, 'wb') as f:
        f.write(content)


if resp["status_code"] == 200:
    # 将抓取的页面转为xpath对象
    html = etree.HTML(resp["text"])
    # 获取文章标题
    title = html.xpath('//a[@class="archive-title"]/text()')
    # 标题图片
    title_img = html.xpath('//div[@class="post-thumb"]/a/img/@src')
    # 下一页
    next_page = html.xpath('//a[@class="next page-numbers"]/@href')
    # print(title, next_page, title_img)
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    start_time = time.time()
    # 异步方式
    tasks = []
    for img in title_img:
        # 准备
        tasks.append(asyncio.ensure_future(download_img(img)))
    # 创建循环事件
    loop = asyncio.get_event_loop()
    # 启动
    loop.run_until_complete(asyncio.wait(tasks))
    # 同步方式
    # for img in title_img:
    #     # 请求图片
    #     res = requests.get(img, headers=headers)
    #     if res.status_code == 200:
    #         # 获取原有名称
    #         name = img.split('/')[-1]
    #         with open(name, 'wb') as f:
    #             f.write(res.content)
    #     else:
    #         print("图片下载失败", img)
    end_time = time.time()
    print("图片下载时间", (end_time - start_time))
    # 同步 - 图片下载时间 4.162432670593262
    # 异步 - 图片下载时间 1.211186408996582
else:
    print("***", resp.status_code)
# 关闭
browser.quit()
