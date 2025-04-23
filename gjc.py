import re
import aiohttp
from lxml import etree
import subprocess
import time
import random
import os

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "https://fj.189.cn/cms/up4/0591/help/1094966.php",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
}

async def get_rs(url, session, json={}, md='', proxy=None):
    """
    支持代理的异步请求函数
    :param url: 请求的URL
    :param session: aiohttp.ClientSession 对象
    :param json: 请求的 JSON 数据
    :param md: 请求方法，'get' 或 'post'
    :param proxy: 代理地址，默认为 None
    :return: 响应结果
    """
    url_title = url.split('//')[0] + '//'
    url_ym = url_title + url.split('/', 3)[2]

    if md != 'post':
        async with session.get(url, proxy=proxy) as response:
            response_text = await response.text()
    else:
        async with session.post(url, json=json, proxy=proxy) as response:
            response_text = await response.text()

    ee = etree.HTML(response_text)
    daima1 = ''.join(ee.xpath("//script/text()")[0])
    content = ee.xpath("//meta/@content")[1]
    src = ee.xpath('//script/@src')[0]
    script_url = url_ym + src

    if os.path.exists('daima2.js'):
        with open('daima2.js', 'r', encoding='utf-8') as daima2_file:
            daima2 = daima2_file.read()
    else:
        async with session.get(script_url, proxy=proxy) as response:
            daima2 = await response.text()
        with open('daima2.js', 'w', encoding='utf-8') as daima2_file:
            daima2_file.write(daima2)

    run_code = daima1 + daima2
    with open('gjc.js', 'r', encoding='utf-8') as file:
        js_code = file.read().replace('replace_contentjs', run_code).replace('replace_content', f"'{content}'")

    file_name = 'result{}.js'.format(time.time() + random.random())
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(js_code)

    result = subprocess.check_output([r'node', file_name])
    try:
        result = result.decode()
    except:
        result = str(result)

    result = result.split(';')[0]
    os.remove(file_name)
    return {result.split('=', 1)[0]: result.split('=', 1)[1]}

async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        json = {
            'ticket': 'ed9780fc85612ac77fc69f22260a44208e421b4249beebcb87b1ce6c959fbdb3ffb0bba12c8234a6e8114bdeaf6307e874147fa167fce00a50652f51529e6a5870d772f634bbcec225f6e5c7c652be1575029ea6a8120199a5644e44f9822569',
            'backUrl': 'https%3A%2F%2Fwapact.189.cn%3A9001',
            'platformCode': 'P201010301',
            'loginType': 2
        }
        # 示例：使用代理
        proxy = "http://your_proxy_url:port"  # 替换为你的代理地址
        cookies = await get_rs('http://wapact.189.cn:9000/gateway/stand/detailNew/exchange', session=session, json={}, md='post', proxy=proxy)
        session.cookie_jar.update_cookies(cookies)
        print(session.cookie_jar.filter_cookies('http://wapact.189.cn:9000'))

        async with session.post('http://wapact.189.cn:9000/gateway/stand/detailNew/exchange', json=json, proxy=proxy) as res:
            print(await res.text())

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())