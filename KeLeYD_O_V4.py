oo0o ='''
cron: 30 */30 8-22 * * *
new Env('可乐阅读');
活动入口：http://12318208252026.excqoef.cn/r?upuid=123182
使用方法：
1.入口,WX打开：http://12318208252026.excqoef.cn/r?upuid=123182
'''#line:7
'''
请仔细阅读下面的使用方式：
1.入口1,WX打开http://12318208252026.excqoef.cn/r?upuid=123182
入口2：http://12318208261109.eooyvuu.cn/r?upuid=123182
若链接微信无法打开，请复制到浏览器复制新链接打开
2.打开活动入口，抓包的任意接口cookie参数
3.青龙菜单项《配置文件》，添加本脚本环境变量
填写变量参数时为方便填写可以随意换行
单账户：export klydconfig="[{'name':'备注名','udtauth12': 'xxxx','key':'xxxxxxx','uids':'xxxxxxx'}]"
多账户：export klydconfig="[
{'name':'备注名','udtauth12': 'xxxx','key':'xxxxx','uids':'xxxxxxx'},
{'name':'备注名','udtauth12': 'xxxx','key':'xxxxxxx','uids':'xxxxxxx'},
{'name':'备注名','udtauth12': 'xxx7Rxxxxx','key':'xxxxxxx','uids':'xxxxxxx'}
]"
参数说明：
name:备注名随意填写
cookie:打开活动入口，抓包的任意接口headers中的udtauth12参数
key：每个账号的推送标准，每个账号全阅读只需要一个key,多个账号需要多个key,key永不过期。
为了防止恶意调用key接口，限制每个ip每天只能获取一个key。手机开飞行模式10s左右可以变更ip重新获取key
通过浏览器打开链接获取:http://175.24.153.42:8882/getkey
uids:wxpusher的参数，当一个微信关注了一个wxpusher的推送应用后，会在推送管理后台(https://wxpusher.zjiecode.com/admin/main)的'用户管理-->用户列表'中显示
用户在推送页面点击’我的-->我的UID‘也可以获取
4.青龙菜单项《配置文件》，添加本脚wxpusher环境变量(不需要重复添加)
export push_config="{'printf':0,'threadingf':1,'threadingt':3,'appToken':'xxxx'}"
参数说明：
printf:0是不打印调试日志，1是打印调试日志
threadingf:并行运行账号参数 1并行执行，0顺序执行，并行执行优点，能够并行跑所以账号，加快完成时间，缺点日志打印混乱。
threadingt:并行运行时每个账号的间隔时间默认3s
appToken 这个是填wxpusher的appToken,wxpusher如何使用可以百度
5.脚本运行时，检测到需要手动阅读的文章，将会推送到你的微信（需要填写好推送参数），你需要手动点击推送，阅读文章，这时脚本会继续运行，否则60秒后将检查超时，停止脚本。
定时运行每半个小时一次
6.优化提现功能，新增支付宝提现共功能
启用支付宝提现，请在青龙菜单项《配置文件》，添加kltx1环境变量
第一个账号变量就是kltx1
第二个账号变量就是kltx2
类似如下
export kltx1="{'name':'李四','phone':'18888888888','limit_tx':50}"
export kltx2="{'name':'李四','phone':'18888888888','limit_tx':50}"
export kltx3="{'name':'李四','phone':'18888888888','limit_tx':50}"
export kltx4="{'name':'李四','phone':'18888888888','limit_tx':50}"
参数说明：
name：支付宝用户姓名
phone：支付宝用户手机号
limit_tx：提现标准，单位为分，不能小于30分。自行参考设置。(仅对支付宝提现生效)
'''#line:52
import requests #line:53
import re #line:54
import random #line:55
import os #line:56
import threading #line:57
import json #line:58
import hashlib #line:59
import time #line:60
from urllib .parse import urlparse ,parse_qs ,quote #line:61
checkDict ={'ischeck':['检测标注','检测标注请勿修改'],'MzkwNTY1MzYxOQ==':['无无有歌','gh_7d594718e309'],}#line:65
push_num =[-1 ]#line:66
def getmsg ():#line:67
    global checkDict #line:68
    O000O00O00O0O0OOO ='v1.4'#line:69
    try :#line:70
        OOOOO0000OO0O0OOO ='http://175.24.153.42:8881/getmsg'#line:71
        O0O00OO00O00OOOOO ={'type':'zhyd'}#line:72
        OOOOOO00O0OOOOO0O =requests .get (OOOOO0000OO0O0OOO ,params =O0O00OO00O00OOOOO ,timeout =2 )#line:73
        O0O0000OO00O00OOO =OOOOOO00O0OOOOO0O .json ()#line:74
        O0OOO0OO0OO000O00 =O0O0000OO00O00OOO .get ('version')#line:75
        OOO0O0OO0OO0O0O00 =O0O0000OO00O00OOO .get ('gdict')#line:76
        OO0000OO000O00O00 =O0O0000OO00O00OOO .get ('gmmsg')#line:77
        print ('系统公告:',OO0000OO000O00O00 )#line:78
        print (f'最新版本{O0OOO0OO0OO000O00},当前版本{O000O00O00O0O0OOO}')#line:79
        if O000O00O00O0O0OOO !=O0OOO0OO0OO000O00 :#line:80
            print ('版本不一致，可能要更新脚本了')#line:81
        print (f'系统的公众号字典{len(OOO0O0OO0OO0O0O00)}个:{OOO0O0OO0OO0O0O00}')#line:82
        print (f'本脚本公众号字典{len(checkDict.values())}个:{list(checkDict.keys())}')#line:83
        checkDict ={}#line:84
        for OO00OOO0000OO0OO0 in OOO0O0OO0OO0O0O00 :#line:85
            checkDict .update ({OO00OOO0000OO0OO0 :['','']})#line:86
    except Exception as O0O000O00O0O00000 :#line:87
        print (O0O000O00O0O00000 )#line:88
        print ('公告服务器异常')#line:89
def push (O0OO00000O0OOO0OO ,OOOO000OO0O0OOOOO ,OO000000OOO00O000 ,OO00OO000O00OO0OO ,O0O000000OOO00O00 ,O00OOOO0O0OO0O0OO ):#line:90
    O0O0O0O00000OOO0O ='''
<body onload="window.location.href='LINK'">
<p>TEXT</p><br>
<p><a href="http://175.24.153.42:8882/lookstatus?key=KEY&type=TYPE">查看状态</a></p><br>
</body>
    '''#line:96
    OOOO000O0000O0OO0 =O0O0O0O00000OOO0O .replace ('TITTLE',O0OO00000O0OOO0OO ).replace ('LINK',OOOO000OO0O0OOOOO ).replace ('TEXT',OO000000OOO00O000 ).replace ('TYPE',OO00OO000O00OO0OO ).replace ('KEY',O00OOOO0O0OO0O0OO )#line:98
    O0O00000O0O0OO00O ={"appToken":appToken ,"content":OOOO000O0000O0OO0 ,"summary":O0OO00000O0OOO0OO ,"contentType":2 ,"uids":[O0O000000OOO00O00 ]}#line:105
    OO0O0O0OOO000OOO0 ='http://wxpusher.zjiecode.com/api/send/message'#line:106
    try :#line:107
        OO0OOOO00O00000OO =requests .post (url =OO0O0O0OOO000OOO0 ,json =O0O00000O0O0OO00O ).text #line:108
        print ('推送结果：',OO0OOOO00O00000OO )#line:109
        return True #line:110
    except Exception as OO00OOO00O0OOOO00 :#line:111
        print ('推送失败！')#line:112
        print ('推送结果：',OO00OOO00O0OOOO00 )#line:113
        return False #line:114
def getinfo (OOO0O0OOOOOOOO00O ):#line:115
    try :#line:116
        OOO0O00OOOO00O00O ={'Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090b19) XWEB/9193 Flue','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Language':'zh-CN,zh;q=0.9','Cookie':'rewardsn=; wxtokenkey=777; devicetype=Windows11x64; version=73020b18; lang=zh_CN;',}#line:123
        O0000OO0OOO0O00O0 =requests .get (OOO0O0OOOOOOOO00O ,headers =OOO0O00OOOO00O00O )#line:124
        O0O0000O0OO0O0OOO =re .sub ('\s','',O0000OO0OOO0O00O0 .text )#line:125
        O0O0OOOOOOOOO00OO =re .findall ('varbiz="(.*?)"\|\|',O0O0000O0OO0O0OOO )#line:126
        if O0O0OOOOOOOOO00OO !=[]:#line:127
            O0O0OOOOOOOOO00OO =O0O0OOOOOOOOO00OO [0 ]#line:128
        if O0O0OOOOOOOOO00OO ==''or O0O0OOOOOOOOO00OO ==[]:#line:129
            if '__biz'in OOO0O0OOOOOOOO00O :#line:130
                O0O0OOOOOOOOO00OO =re .findall ('__biz=(.*?)&',OOO0O0OOOOOOOO00O )#line:131
                if O0O0OOOOOOOOO00OO !=[]:#line:132
                    O0O0OOOOOOOOO00OO =O0O0OOOOOOOOO00OO [0 ]#line:133
        O0O0OOO0OO000OOO0 =re .findall ('varnickname=htmlDecode\("(.*?)"\);',O0O0000O0OO0O0OOO )#line:134
        if O0O0OOO0OO000OOO0 !=[]:#line:135
            O0O0OOO0OO000OOO0 =O0O0OOO0OO000OOO0 [0 ]#line:136
        OO0O000O0OO0O00O0 =re .findall ('varuser_name="(.*?)";',O0O0000O0OO0O0OOO )#line:137
        if OO0O000O0OO0O00O0 !=[]:#line:138
            OO0O000O0OO0O00O0 =OO0O000O0OO0O00O0 [0 ]#line:139
        OO0O0O000OOO00O00 =re .findall ("varmsg_title='(.*?)'\.html\(",O0O0000O0OO0O0OOO )#line:140
        if OO0O0O000OOO00O00 !=[]:#line:141
            OO0O0O000OOO00O00 =OO0O0O000OOO00O00 [0 ]#line:142
        OO000O0O0000OOOO0 =re .findall ("varoriCreateTime='(.*?)';",O0O0000O0OO0O0OOO )#line:143
        if OO000O0O0000OOOO0 !=[]:#line:144
            OO000O0O0000OOOO0 =OO000O0O0000OOOO0 [0 ]#line:145
        OOOO0O000000OOO00 =re .findall ("varcreateTime='(.*?)';",O0O0000O0OO0O0OOO )#line:146
        if OOOO0O000000OOO00 !=[]:#line:147
            OOOO0O000000OOO00 =OOOO0O000000OOO00 [0 ]#line:148
            OOOO0O000000OOO00 =OOOO0O000000OOO00 [:-5 ]+' '+OOOO0O000000OOO00 [-5 :]#line:149
        O0000O00O0OOO00O0 =f'公众号唯一标识：{O0O0OOOOOOOOO00OO}|文章:{OO0O0O000OOO00O00}|作者:{O0O0OOO0OO000OOO0}|账号:{OO0O000O0OO0O00O0}|文章时间戳:{OO000O0O0000OOOO0}|文章时间:{OOOO0O000000OOO00}'#line:150
        print (O0000O00O0OOO00O0 )#line:151
        return O0O0OOO0OO000OOO0 ,OO0O000O0OO0O00O0 ,OO0O0O000OOO00O00 ,O0000O00O0OOO00O0 ,O0O0OOOOOOOOO00OO ,OO000O0O0000OOOO0 ,OOOO0O000000OOO00 #line:152
    except Exception as O00OOOOOOOO0OOOOO :#line:153
        print (O00OOOOOOOO0OOOOO )#line:154
        print ('异常')#line:155
        return False #line:156
class WXYD :#line:157
    def __init__ (O00O0O0OO00O0OO0O ,OOOOOOOOO0OOOOO0O ,OOOO0O0O00O00OOO0 ):#line:158
        O00O0O0OO00O0OO0O .indexs =str (OOOO0O0O00O00OOO0 +1 )#line:159
        O00O0O0OO00O0OO0O .name =OOOOOOOOO0OOOOO0O ['name']#line:160
        O00O0O0OO00O0OO0O .key =OOOOOOOOO0OOOOO0O ['key']#line:161
        O00O0O0OO00O0OO0O .uids =OOOOOOOOO0OOOOO0O ['uids']#line:162
        O00O0O0OO00O0OO0O .count =0 #line:163
        O00O0O0OO00O0OO0O .User_Agent ='Mozilla/5.0 (Linux; Android 13; M2104K10AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110017 MMWEBSDK/20231002 MMWEBID/2545 MicroMessenger/8.0.43.2480(0x28112BE1) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64'#line:164
        OO0O0O00O0O00OOO0 =O00O0O0OO00O0OO0O .get_host ()#line:165
        O00O0O0OO00O0OO0O .host =OO0O0O00O0O00OOO0 [0 ]#line:166
        O00O0O0OO00O0OO0O .t =OO0O0O00O0O00OOO0 [1 ]#line:167
        O00O0O0OO00O0OO0O .headers ={'Host':'m.zzyi4cf7z8.cn','Connection':'keep-alive','Accept':'application/json, text/plain, */*','X-Requested-With':'XMLHttpRequest','udtauth12':OOOOOOOOO0OOOOO0O ['udtauth12'],'User-Agent':O00O0O0OO00O0OO0O .User_Agent ,'Origin':f'http://{O00O0O0OO00O0OO0O.host}','Sec-Fetch-Site':'cross-site','Sec-Fetch-Mode':'cors','Sec-Fetch-Dest':'empty','Referer':f'http://{O00O0O0OO00O0OO0O.host}/','Accept-Encoding':'gzip, deflate, br','Accept-Language':'zh-CN,zh;q=0.9',}#line:182
    def printjson (O00OO00OO0OOO0OO0 ,O00OO0OOO0O0OO000 ):#line:183
        if printf ==0 :#line:184
            return False #line:185
        print (O00OO00OO0OOO0OO0 .name ,O00OO0OOO0O0OO000 )#line:186
    def setstatus (OOOOO0OO000O0OO00 ):#line:187
        try :#line:188
            O00O00O000OO0O0OO ='http://175.24.153.42:8882/setstatus'#line:189
            O0OOOOO0O000O0000 ={'key':OOOOO0OO000O0OO00 .key ,'type':'zhyd','val':'1','ven':oo0o }#line:190
            OO000O0OOOOO0OOO0 =requests .get (O00O00O000OO0O0OO ,params =O0OOOOO0O000O0000 ,timeout =5 )#line:191
            print (OOOOO0OO000O0OO00 .name ,OO000O0OOOOO0OOO0 .text )#line:192
            if '无效'in OO000O0OOOOO0OOO0 .text :#line:193
                exit (0 )#line:194
        except Exception as O0000O000O0OO00O0 :#line:195
            print (OOOOO0OO000O0OO00 .name ,'设置状态异常')#line:196
            print (OOOOO0OO000O0OO00 .name ,O0000O000O0OO00O0 )#line:197
            return 99 #line:198
    def getstatus (OOOOO00O000OOOO00 ):#line:199
        try :#line:200
            O0O00000O000000OO ='http://175.24.153.42:8882/getstatus'#line:201
            OOOOOO0O0OO00000O ={'key':OOOOO00O000OOOO00 .key ,'type':'zhyd'}#line:202
            O00OOO0000OOO00O0 =requests .get (O0O00000O000000OO ,params =OOOOOO0O0OO00000O ,timeout =3 )#line:203
            return O00OOO0000OOO00O0 .text #line:204
        except Exception as O0000O0O000OOOOOO :#line:205
            print (OOOOO00O000OOOO00 .name ,'查询状态异常',O0000O0O000OOOOOO )#line:206
            return False #line:207
    def get_host (O0O0000O000O000O0 ):#line:208
        try :#line:209
            OO0O0O0O0O0OOO0O0 ='http://12318208252026.excqoef.cn/r?upuid=123182'#line:210
            O0O00OO0OO00O00OO ={'Host':'12318208252026.excqoef.cn','Connection':'keep-alive','Upgrade-Insecure-Requests':'1','User-Agent':O0O0000O000O000O0 .User_Agent ,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9',}#line:219
            O0OO0OOOOOO0O0OOO =requests .get (OO0O0O0O0O0OOO0O0 ,headers =O0O00OO0OO00O00OO ,allow_redirects =False )#line:220
            if O0OO0OOOOOO0O0OOO .headers .get ('Location')!=None :#line:221
                OO0O000OO0OO0000O =urlparse (O0OO0OOOOOO0O0OOO .headers .get ('Location'))#line:222
                O00O0OO0OOOO0O0OO =OO0O000OO0OO0000O .netloc #line:223
                O00OOO00O0O0OOO00 =re .findall (r't=(\d+)',O0OO0OOOOOO0O0OOO .headers .get ('Location'))[0 ]#line:224
                return O00O0OO0OOOO0O0OO ,O00OOO00O0O0OOO00 #line:225
            else :#line:226
                print ('获取host失败0')#line:227
                return 'klluodi-04.obs.cn-jxnc1.ctyun.cn'#line:228
        except Exception as OO000000OOO00000O :#line:229
            print ('获取host失败1',OO000000OOO00000O )#line:230
            return 'klluodi-04.obs.cn-jxnc1.ctyun.cn'#line:231
    def tuijian (OOOOO0OO0OOO0OO0O ):#line:232
        O0000OOO00O0OO000 =f'https://m.zzyi4cf7z8.cn/tuijian?url=upuid%3D123182%26t%3D{OOOOO0OO0OOO0OO0O.t}&upuid=123182'#line:233
        OO0O0OO00O0O00000 =requests .get (O0000OOO00O0OO000 ,headers =OOOOO0OO0OOO0OO0O .headers )#line:234
        try :#line:235
            OOOOOO0000000O000 =OO0O0OO00O0O00000 .json ()#line:236
            if OOOOOO0000000O000 .get ('code')==0 :#line:237
                OO0OOOOOOOO0O0OO0 =OOOOOO0000000O000 ['data']['user']['username']#line:238
                O00OOO00000O00O00 =float (OOOOOO0000000O000 ['data']['user']['score'])/100 #line:239
                OO00O000OO00OO0OO =OOOOOO0000000O000 ['data']['infoView'].get ('msg')#line:240
                O0OOO0000O00O0O00 =OOOOOO0000000O000 ['data']['infoView']['num']#line:241
                O00O0000O00OO0O00 =OOOOOO0000000O000 ['data']['infoView']['rest']#line:242
                if O00O0000O00OO0O00 ==0 :#line:243
                    print ('当前状态，可能是不可阅读')#line:244
                    print (OOOOO0OO0OOO0OO0O .name ,f'{OO0OOOOOOOO0O0OO0}:当前剩余{O00OOO00000O00O00}元,今日已经阅读：{O0OOO0000O00O0O00}篇,提示信息：{OO00O000OO00OO0OO}')#line:245
                    return False #line:246
                print (OOOOO0OO0OOO0OO0O .name ,f'{OO0OOOOOOOO0O0OO0}:当前剩余{O00OOO00000O00O00}元,今日已经阅读：{O0OOO0000O00O0O00}篇,提示信息：{OO00O000OO00OO0OO}')#line:247
                return True #line:248
            else :#line:249
                print (OOOOO0OO0OOO0OO0O .name ,OOOOOO0000000O000 )#line:250
                print (OOOOO0OO0OOO0OO0O .name ,'账号异常0,ck可能失效')#line:251
                return False #line:252
        except Exception as OO00OOO0O0OO0OOO0 :#line:253
            print (OOOOO0OO0OOO0OO0O .name ,OO00OOO0O0OO0OOO0 )#line:254
            print (OOOOO0OO0OOO0OO0O .name ,'账号异常1，ck可能失效')#line:255
            return False #line:256
    def get_read_url (OO00O0OO00OOO0O00 ):#line:257
        O000OO000O0O000OO ='https://m.zzyi4cf7z8.cn/new/bbbbb'#line:258
        OO0OO0O0OO0OOOOOO =requests .get (O000OO000O0O000OO ,headers =OO00O0OO00OOO0O00 .headers )#line:259
        O0OOO0O0OO00OOOO0 =OO0OO0O0OO0OOOOOO .json ()#line:260
        O00OOOO0000000O0O =O0OOO0O0OO00OOOO0 .get ('jump')#line:261
        O0OO0OO0O0OOO0OOO =parse_qs (urlparse (O00OOOO0000000O0O ).query )#line:262
        O00O00OO0000000O0 =urlparse (O00OOOO0000000O0O ).netloc #line:263
        OOO000000O0OO0O00 =O0OO0OO0O0OOO0OOO .get ('iu')[0 ]#line:264
        O000OOOOOOOOO0OO0 ={'Host':OO00O0OO00OOO0O00 .host ,'Connection':'keep-alive','User-Agent':OO00O0OO00OOO0O00 .User_Agent ,'X-Requested-With':'XMLHttpRequest','Accept':'*/*','Origin':f'http://{O00O00OO0000000O0}','Sec-Fetch-Site':'cross-site','Sec-Fetch-Mode':'cors','Sec-Fetch-Dest':'empty','Referer':f'http://{O00O00OO0000000O0}/','Accept-Encoding':'gzip, deflate, br','Accept-Language':'zh-CN,zh;q=0.9',}#line:278
        return OOO000000O0OO0O00 ,O00O00OO0000000O0 ,O000OOOOOOOOO0OO0 #line:279
    def do_read (O0OOO00O00O0OO0O0 ):#line:281
        O0OOO00OOO0O0O0O0 =O0OOO00O00O0OO0O0 .get_read_url ()#line:282
        O0OOO00O00O0OO0O0 .jkey =''#line:283
        OOOOO00OO00O0O0OO =0 #line:284
        while True :#line:285
            OOO0000OO0O0OO00O =f'iu={O0OOO00OOO0O0O0O0[0]}&r={round(random.uniform(0, 1), 17)}&{O0OOO00O00O0OO0O0.jkey}'#line:287
            OOO00O0O000OOOOO0 ='https://m.zzyi4cf7z8.cn/dodoaa/mmaa?'+OOO0000OO0O0OO00O #line:288
            O0OOO00O00O0OO0O0 .printjson (OOO00O0O000OOOOO0 )#line:289
            O0OOOOO000000O0O0 =requests .get (OOO00O0O000OOOOO0 ,headers =O0OOO00OOO0O0O0O0 [2 ])#line:290
            print (O0OOO00O00O0OO0O0 .name ,'-'*50 )#line:291
            OO00OO00OO00O0OOO =O0OOOOO000000O0O0 .json ()#line:292
            if OO00OO00OO00O0OOO .get ('msg'):#line:293
                print (O0OOO00O00O0OO0O0 .name ,'弹出msg',OO00OO00OO00O0OOO .get ('msg'))#line:294
            if OO00OO00OO00O0OOO .get ('success_msg'):#line:295
                print (O0OOO00O00O0OO0O0 .name ,'成功msg',OO00OO00OO00O0OOO .get ('msg'))#line:296
            OOO0O0O0O00O0000O =OO00OO00OO00O0OOO .get ('url')#line:297
            O0OOO00O00O0OO0O0 .printjson (OOO0O0O0O00O0000O )#line:298
            if OOO0O0O0O00O0000O =='close':#line:299
                print (O0OOO00O00O0OO0O0 .name ,f'阅读结果结束')#line:300
                return True #line:301
            if 'http'in OOO0O0O0O00O0000O :#line:302
                OOOOO00OO00O0O0OO +=1 #line:303
                print (O0OOO00O00O0OO0O0 .name ,f'上一篇阅读结果：{OO00OO00OO00O0OOO.get("success_msg","第一篇开始阅读或者异常")}')#line:304
                OO000OO0000OO0OO0 =OO00OO00OO00O0OOO .get ('jkey')#line:305
                O0OOO00O00O0OO0O0 .jkey =f'&jkey={OO000OO0000OO0OO0}'#line:306
                O00O000OOOOOO000O =getinfo (OOO0O0O0O00O0000O )#line:307
                if OOOOO00OO00O0O0OO in push_num :#line:308
                    O00O0OO00000OOO00 =list (O00O000OOOOOO000O )#line:309
                    O00O0OO00000OOO00 [4 ]='ischeck'#line:310
                    if O0OOO00O00O0OO0O0 .testCheck (O00O0OO00000OOO00 ,OOO0O0O0O00O0000O )==False :#line:311
                        return False #line:312
                else :#line:313
                    if O0OOO00O00O0OO0O0 .testCheck (O00O000OOOOOO000O ,OOO0O0O0O00O0000O )==False :#line:314
                        return False #line:315
                if O0OOO00O00O0OO0O0 .count >=5 :#line:316
                    print (O0OOO00O00O0OO0O0 .name ,'过检测超过4次中止阅读')#line:317
                    return False #line:318
                O0OO000OOOOO0OOOO =random .randint (6 ,9 )#line:319
                print (O0OOO00O00O0OO0O0 .name ,f'本次模拟读{O0OO000OOOOO0OOOO}秒')#line:320
                time .sleep (O0OO000OOOOO0OOOO )#line:321
            else :#line:322
                print (O0OOO00O00O0OO0O0 .name ,'未知结果')#line:323
                print (O0OOO00O00O0OO0O0 .name ,OO00OO00OO00O0OOO )#line:324
                if 'error_html'in O0OOOOO000000O0O0 .text :#line:325
                    print ('阅读异常，可能是IP问题，请手动阅读几篇后在尝试运行脚本')#line:326
                return False #line:327
    def testCheck (OO000000O0000OO00 ,O000000O0OO00OOO0 ,OO0O0OO000O000OOO ):#line:328
        if O000000O0OO00OOO0 [4 ]==[]:#line:329
            print (OO000000O0000OO00 .name ,'这个链接没有获取到微信号id',OO0O0OO000O000OOO )#line:330
            return True #line:331
        if O000000O0OO00OOO0 [5 ]==[]:#line:332
            print (OO000000O0000OO00 .name ,'这个链接没有获取到时间',OO0O0OO000O000OOO )#line:333
            return True #line:334
        if (checkDict .get (O000000O0OO00OOO0 [4 ])!=None )or (int (time .time ())-int (O000000O0OO00OOO0 [5 ])>3600 *24 *14 ):#line:335
            OO000000O0000OO00 .count +=1 #line:336
            if OO000000O0000OO00 .setstatus ()==99 :#line:337
                print (OO000000O0000OO00 .name ,'过检测服务器异常，使用无回调方案，请在50s内阅读检测文章')#line:338
                push (f'可乐阅读过检测:{OO000000O0000OO00.name}',OO0O0OO000O000OOO ,O000000O0OO00OOO0 [3 ],'zhyd',OO000000O0000OO00 .uids ,OO000000O0000OO00 .key )#line:339
                time .sleep (50 )#line:340
                return True #line:341
            for O00O00OOOO0O0OOO0 in range (60 ):#line:342
                if O00O00OOOO0O0OOO0 %30 ==0 :#line:343
                    O0O0OOOOOO0OO0O0O =f'http://175.24.153.42:8882/lookwxarticle?key=KEY&type=TYPE&wxurl={OO0O0OO000O000OOO}'#line:344
                    push (f'可乐阅读过检测:{OO000000O0000OO00.name}',O0O0OOOOOO0OO0O0O ,O000000O0OO00OOO0 [3 ],'zhyd',OO000000O0000OO00 .uids ,OO000000O0000OO00 .key )#line:345
                OOO0000O0OOO0O000 =OO000000O0000OO00 .getstatus ()#line:346
                if OOO0000O0OOO0O000 =='0':#line:347
                    print (OO000000O0000OO00 .name ,'过检测文章已经阅读')#line:348
                    return True #line:349
                elif OOO0000O0OOO0O000 =='1':#line:350
                    print (OO000000O0000OO00 .name ,f'正在等待过检测文章阅读结果{O00O00OOOO0O0OOO0}秒。。。')#line:351
                    time .sleep (1 )#line:352
                else :#line:353
                    print (OO000000O0000OO00 .name ,OOO0000O0OOO0O000 )#line:354
                    print (OO000000O0000OO00 .name ,'服务器异常')#line:355
            print (OO000000O0000OO00 .name ,'过检测超时中止脚本防止黑号')#line:356
            return False #line:357
        else :#line:358
            return True #line:359
    def withdrawal (O0O00O0O0000OO00O ):#line:360
        OO0O00O0O000O00OO ='https://m.zzyi4cf7z8.cn/withdrawal'#line:361
        O00000OOOOOO0OO0O =requests .get (OO0O00O0O000O00OO ,headers =O0O00O0O0000OO00O .headers )#line:362
        O0OO00OOO00O0O0OO =O00000OOOOOO0OO0O .json ()#line:363
        time .sleep (3 )#line:364
        if O0OO00OOO00O0O0OO .get ('code')==0 :#line:365
            O000O0O00O00O00O0 =int (float (O0OO00OOO00O0O0OO ['data']['user']['score']))#line:366
            if O000O0O00O00O00O0 <30 :#line:367
                print ('没有达到提现标标准')#line:368
                return False #line:369
            if O000O0O00O00O00O0 >=2000 :#line:370
                O000O0O00O00O00O0 =2000 #line:371
            OO00O0OO00OO0OO00 =O0O00O0O0000OO00O .headers .copy ()#line:372
            OO00O0OO00OO0OO00 .update ({'Content-Type':'application/x-www-form-urlencoded'})#line:373
            OOO0OOO0O0OO0OO00 =os .getenv ('kltx'+O0O00O0O0000OO00O .indexs )#line:374
            if OOO0OOO0O0OO0OO00 ==None :#line:375
                print ('没有获取到设置的支付宝参数，使用微信提现')#line:376
                O0OOO0OOO0OO0O0O0 =f'amount={O000O0O00O00O00O0}&type=wx'#line:377
            else :#line:378
                OO0O0O0000000OOOO =json .loads (OOO0OOO0O0OO0OO00 .replace ("'",'"'))#line:379
                if O000O0O00O00O00O0 <int (OO0O0O0000000OOOO .get ('limit_tx')):#line:380
                    print ('没有达到你设置的提现标标准')#line:381
                    return False #line:382
                O0OOO0OOO0OO0O0O0 =f'amount={O000O0O00O00O00O0}&type=ali&u_ali_account={OO0O0O0000000OOOO.get("phone")}&u_ali_real_name={quote(OO0O0O0000000OOOO.get("name"))}'#line:383
            OO0O00O0O000O00OO ='https://m.zzyi4cf7z8.cn/withdrawal/doWithdraw'#line:384
            O00000OOOOOO0OO0O =requests .post (OO0O00O0O000O00OO ,headers =OO00O0OO00OO0OO00 ,data =O0OOO0OOO0OO0O0O0 )#line:385
            print (O0O00O0O0000OO00O .name ,'提现结果',O00000OOOOOO0OO0O .text )#line:386
        else :#line:387
            print ('提现异常')#line:388
            print (O0O00O0O0000OO00O .name ,O0OO00OOO00O0O0OO )#line:389
    def run (OOO0000000O000OO0 ):#line:390
        if hashlib .md5 (oo0o .encode ()).hexdigest ()!='e08ca2eddd87fc6ddceba5e5491202bd':OOO0000000O000OO0 .setstatus ()#line:391
        if OOO0000000O000OO0 .tuijian ():#line:392
            time .sleep (2 )#line:393
            OOO0000000O000OO0 .get_read_url ()#line:394
            OOO0000000O000OO0 .do_read ()#line:395
            time .sleep (2 )#line:396
            OOO0000000O000OO0 .tuijian ()#line:397
            time .sleep (2 )#line:398
            OOO0000000O000OO0 .withdrawal ()#line:399
def getEnv (OO000OO0O00O00OO0 ):#line:400
    O0O00OO0OOO0OO0O0 =os .getenv (OO000OO0O00O00OO0 )#line:401
    if O0O00OO0OOO0OO0O0 ==None :#line:402
        print (f'{OO000OO0O00O00OO0}青龙变量里没有获取到')#line:403
        return False #line:404
    try :#line:405
        O0O00OO0OOO0OO0O0 =json .loads (O0O00OO0OOO0OO0O0 .replace ("'",'"').replace ("\n","").replace (" ","").replace ("\t",""))#line:406
        return O0O00OO0OOO0OO0O0 #line:407
    except Exception as OOO0O0O00OOOO000O :#line:408
        print ('错误:',OOO0O0O00OOOO000O )#line:409
        print ('你填写的变量是:',O0O00OO0OOO0OO0O0 )#line:410
        print ('请检查变量参数是否填写正确')#line:411
if __name__ =='__main__':#line:412
    push_config =getEnv ('push_config')#line:414
    klydconfig =getEnv ('klydconfig')#line:415
    printf =push_config .get ('printf',0 )#line:416
    appToken =push_config ['appToken']#line:417
    threadingf =push_config .get ('threadingf',1 )#line:418
    getmsg ()#line:419
    if threadingf ==1 :#line:420
        tl =[]#line:421
        for indexs ,cg in enumerate (klydconfig ):#line:422
            print ('*'*50 )#line:423
            print (f'开始执行{cg["name"]}')#line:424
            api =WXYD (cg ,indexs )#line:425
            t =threading .Thread (target =api .run ,args =())#line:426
            tl .append (t )#line:427
            t .start ()#line:428
            threadingt =push_config .get ('threadingt',3 )#line:429
            time .sleep (threadingt )#line:430
        for t in tl :#line:431
            t .join ()#line:432
    elif threadingf ==0 :#line:433
        for indexs ,cg in enumerate (klydconfig ):#line:434
            print ('*'*50 )#line:435
            print (f'开始执行{cg["name"]}')#line:436
            api =WXYD (cg ,indexs )#line:437
            api .run ()#line:438
            print (f'{cg["name"]}执行完毕')#line:439
            time .sleep (3 )#line:440
    else :#line:441
        print ('请确定推送变量中threadingf参数是否正确')#line:442
    print ('全部账号执行完成')#line:443
    time .sleep (10 )#line:444
