oo0o ='''
cron: 10 */30 8-22 * * *
new Env('f小阅阅阅读');
活动入口：http://8940181308_ybb0a.qlymyxgsfc370.cn/ustgtmps/868cd99e0d7d5e0e034bd4f421c0587f?uid=62
'''#line:5
'''
使用方法：
1.微信打开活动入口：http://8940181308_ybb0a.qlymyxgsfc370.cn/ustgtmps/868cd99e0d7d5e0e034bd4f421c0587f?uid=62
2.抓包的任意接口cookies中的ysmuid参数
3.青龙菜单项《配置文件》，添加本脚本环境变量
填写变量参数时为方便填写可以随意换行
单账户：export xyyconfig="[{'name':'备注名','ysmuid': 'xxxx','key':'xxxxxxx','uids':'xxxxxxx'}]"
多账户：export xyyconfig="[
{'name':'备注名','ysmuid': 'xxxx','key':'xxxxx','uids':'xxxxxxx'},
{'name':'备注名','ysmuid': 'xxxx','key':'xxxxxxx','uids':'xxxxxxx'},
{'name':'备注名','ysmuid': 'xxxx','key':'xxxxxxx','uids':'xxxxxxx'}
]"参数说明与获取：
name:备注名随意填写
ysmuid:抓包的任意接口cookies中的ysmuid参数,
key:每个账号的推送标准，每个账号全阅读只需要一个key,多个账号需要多个key,key永不过期。
为了防止恶意调用key接口，限制每个ip每天只能获取一个key。手机开飞行模式10s左右可以变更ip重新获取key
通过浏览器打开链接获取:http://175.24.153.42:8882/getkey
uids:wxpusher的参数，当一个微信关注了一个wxpusher的推送应用后，会在推送管理后台(https://wxpusher.zjiecode.com/admin/main)的'用户管理-->用户列表'中显示
用户在推送页面点击’我的-->我的UID‘也可以获取
4.青龙环境变量菜单，添加本脚wxpusher环境变量(不需要重复添加)
青名称 ：push_config
参数 ：{"printf":0,"threadingf":1,"appToken":"xxxx"}
例如：{"printf":0,"threadingf":1,"appToken":"AT_r1vNXQdfgxxxxxscPyoORYg"}
参数说明：
printf 0是不打印调试日志，1是打印调试日志
threadingf:并行运行账号参数 1并行执行，0顺序执行，并行执行优点，能够并行跑所以账号，加快完成时间，缺点日志打印混乱。
appToken 这个是填wxpusher的appToken
5.提现标准默认是3000
'''#line:34
import time #line:36
import requests #line:37
import random #line:38
import re #line:39
import os #line:40
import json #line:41
import threading #line:42
import hashlib #line:43
from urllib .parse import urlparse ,parse_qs #line:44
checkDict ={'MzkxNTE3MzQ4MQ==':['香姐爱旅行','gh_54a65dc60039'],'Mzg5MjM0MDEwNw==':['我本非凡','gh_46b076903473'],'MzUzODY4NzE2OQ==':['多肉葡萄2020','gh_b3d79cd1e1b5'],'MzkyMjE3MzYxMg==':['Youhful','gh_b3d79cd1e1b5'],'MzkxNjMwNDIzOA==':['少年没有乌托邦3','gh_b3d79cd1e1b5'],'Mzg3NzUxMjc5Mg==':['星星诺言','gh_b3d79cd1e1b5'],'Mzg4NTcwODE1NA==':['斑马还没睡123','gh_b3d79cd1e1b5'],'Mzk0ODIxODE4OQ==':['持家妙招宝典','gh_b3d79cd1e1b5'],'Mzg2NjUyMjI1NA==':['Lilinng','gh_b3d79cd1e1b5'],'MzIzMDczODg4Mw==':['有故事的同学Y','gh_b3d79cd1e1b5'],'Mzg5ODUyMzYzMQ==':['789也不行','gh_b3d79cd1e1b5'],'MzU0NzI5Mjc4OQ==':['皮蛋瘦肉猪','gh_58d7ee593b86'],'Mzg5MDgxODAzMg==':['北北小助手','gh_58d7ee593b86'],'MzkxNDU1NDEzNw==':['小阅阅服务','gh_e50cfefef9e5'],}#line:62
def getmsg ():#line:63
    global checkDict #line:64
    OOOO0OO0O0O0O00OO ='v1.1'#line:65
    try :#line:66
        OOO0O0O0OO0O0OOO0 ='http://175.24.153.42:8881/getmsg'#line:67
        O00OO0OO0O00O00O0 ={'type':'xyyyd'}#line:68
        O00O000O0OOOO0000 =requests .get (OOO0O0O0OO0O0OOO0 ,params =O00OO0OO0O00O00O0 ,timeout =2 )#line:69
        OOO0OO00O00O0O0OO =O00O000O0OOOO0000 .json ()#line:70
        O0OOO00O0O0O0O00O =OOO0OO00O00O0O0OO .get ('version')#line:71
        OO00O0OOOO000O0O0 =OOO0OO00O00O0O0OO .get ('gdict')#line:72
        OO0OO0OOO0OOOOO00 =OOO0OO00O00O0O0OO .get ('gmmsg')#line:73
        print ('系统公告:',OO0OO0OOO0OOOOO00 )#line:74
        print (f'最新版本{O0OOO00O0O0O0O00O},当前版本{OOOO0OO0O0O0O00OO}')#line:75
        if OOOO0OO0O0O0O00OO !=O0OOO00O0O0O0O00O :#line:76
            print ('版本不一致，可能要更新脚本了')#line:77
        print (f'系统的公众号字典{len(OO00O0OOOO000O0O0)}个:{OO00O0OOOO000O0O0}')#line:78
        print (f'本脚本公众号字典{len(checkDict.values())}个:{list(checkDict.keys())}')#line:79
        checkDict ={}#line:80
        for O00OOOOO00O0000OO in OO00O0OOOO000O0O0 :#line:81
            checkDict .update ({O00OOOOO00O0000OO :['','']})#line:82
    except Exception as O0OOO0OO0OOOOOO0O :#line:83
        print (O0OOO0OO0OOOOOO0O )#line:84
        print ('公告服务器异常')#line:85
def push (O0OO000OO0OO0OO00 ,OOOO00O00O0O00OO0 ,O0000O0O0000O0O0O ,O0O0000000O0O00O0 ,O0OO000O0000O000O ,O0OO00O000000O000 ):#line:88
    O0O0000O0OOOOO0OO ='''
<body onload="window.location.href='LINK'">
<p>TEXT</p><br>
<p><a href="http://175.24.153.42:8882/lookstatus?key=KEY&type=TYPE">查看状态</a></p><br>
</body>
    '''#line:94
    OO000000O0O000O0O =O0O0000O0OOOOO0OO .replace ('TITTLE',O0OO000OO0OO0OO00 ).replace ('LINK',OOOO00O00O0O00OO0 ).replace ('TEXT',O0000O0O0000O0O0O ).replace ('TYPE',O0O0000000O0O00O0 ).replace ('KEY',O0OO00O000000O000 )#line:96
    O00000OOO0OOOOOOO ={"appToken":appToken ,"content":OO000000O0O000O0O ,"summary":O0OO000OO0OO0OO00 ,"contentType":2 ,"uids":[O0OO000O0000O000O ]}#line:103
    O00OO0OO000OO00OO ='http://wxpusher.zjiecode.com/api/send/message'#line:104
    try :#line:105
        O00000OO0O000O000 =requests .post (url =O00OO0OO000OO00OO ,json =O00000OOO0OOOOOOO ).text #line:106
        print ('推送结果：',O00000OO0O000O000 )#line:107
        return True #line:108
    except Exception as OO0O00000O000O0O0 :#line:109
        print ('推送失败！')#line:110
        print ('推送结果：',OO0O00000O000O0O0 )#line:111
        return False #line:112
def getinfo (O0O000O00OOOO000O ):#line:113
    try :#line:114
        OOO0O0O000OO00O0O ={'Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090b19) XWEB/9193 Flue','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Language':'zh-CN,zh;q=0.9','Cookie':'rewardsn=; wxtokenkey=777; devicetype=Windows11x64; version=73020b18; lang=zh_CN;',}#line:121
        O0OOOO0O0OOO0OOOO =requests .get (O0O000O00OOOO000O ,headers =OOO0O0O000OO00O0O )#line:122
        O0O00000OOO0OO000 =re .sub ('\s','',O0OOOO0O0OOO0OOOO .text )#line:123
        O0O000O0OOOOO0O00 =re .findall ('varbiz="(.*?)"\|\|',O0O00000OOO0OO000 )#line:124
        if O0O000O0OOOOO0O00 !=[]:#line:125
            O0O000O0OOOOO0O00 =O0O000O0OOOOO0O00 [0 ]#line:126
        if O0O000O0OOOOO0O00 ==''or O0O000O0OOOOO0O00 ==[]:#line:127
            if '__biz'in O0O000O00OOOO000O :#line:128
                O0O000O0OOOOO0O00 =re .findall ('__biz=(.*?)&',O0O000O00OOOO000O )#line:129
                if O0O000O0OOOOO0O00 !=[]:#line:130
                    O0O000O0OOOOO0O00 =O0O000O0OOOOO0O00 [0 ]#line:131
        O00OOO000O0O00OO0 =re .findall ('varnickname=htmlDecode\("(.*?)"\);',O0O00000OOO0OO000 )#line:132
        if O00OOO000O0O00OO0 !=[]:#line:133
            O00OOO000O0O00OO0 =O00OOO000O0O00OO0 [0 ]#line:134
        O0OO00000O00O0OOO =re .findall ('varuser_name="(.*?)";',O0O00000OOO0OO000 )#line:135
        if O0OO00000O00O0OOO !=[]:#line:136
            O0OO00000O00O0OOO =O0OO00000O00O0OOO [0 ]#line:137
        OO000OO00O0OOO0O0 =re .findall ("varmsg_title='(.*?)'\.html\(",O0O00000OOO0OO000 )#line:138
        if OO000OO00O0OOO0O0 !=[]:#line:139
            OO000OO00O0OOO0O0 =OO000OO00O0OOO0O0 [0 ]#line:140
        OOO0O0000O000O000 =re .findall ("varoriCreateTime='(.*?)';",O0O00000OOO0OO000 )#line:141
        if OOO0O0000O000O000 !=[]:#line:142
            OOO0O0000O000O000 =OOO0O0000O000O000 [0 ]#line:143
        O0O00O0O000OO0000 =re .findall ("varcreateTime='(.*?)';",O0O00000OOO0OO000 )#line:144
        if O0O00O0O000OO0000 !=[]:#line:145
            O0O00O0O000OO0000 =O0O00O0O000OO0000 [0 ]#line:146
            O0O00O0O000OO0000 =O0O00O0O000OO0000 [:-5 ]+' '+O0O00O0O000OO0000 [-5 :]#line:147
        O0O000OO000000000 =f'公众号唯一标识：{O0O000O0OOOOO0O00}|文章:{OO000OO00O0OOO0O0}|作者:{O00OOO000O0O00OO0}|账号:{O0OO00000O00O0OOO}|文章时间戳:{OOO0O0000O000O000}|文章时间:{O0O00O0O000OO0000}'#line:148
        print (O0O000OO000000000 )#line:149
        return O00OOO000O0O00OO0 ,O0OO00000O00O0OOO ,OO000OO00O0OOO0O0 ,O0O000OO000000000 ,O0O000O0OOOOO0O00 ,OOO0O0000O000O000 ,O0O00O0O000OO0000 #line:150
    except Exception as O000O00000OO00O0O :#line:151
        print (O000O00000OO00O0O )#line:152
        print ('异常')#line:153
        return False #line:154
def ts ():#line:157
    return str (int (time .time ()))+'000'#line:158
class HHYD ():#line:161
    def __init__ (OO000OO000OO0OOO0 ,O0000000OO00O0OO0 ):#line:162
        OO000OO000OO0OOO0 .name =O0000000OO00O0OO0 ['name']#line:163
        OO000OO000OO0OOO0 .ysmuid =O0000000OO00O0OO0 ['ysmuid']#line:164
        OO000OO000OO0OOO0 .key =O0000000OO00O0OO0 ['key']#line:165
        OO000OO000OO0OOO0 .uids =O0000000OO00O0OO0 ['uids']#line:166
    def setstatus (OOOO000O000OOO0O0 ):#line:168
        try :#line:169
            OOO00O0000000OOO0 ='http://175.24.153.42:8882/setstatus'#line:170
            OO00O000O00O0O0OO ={'key':OOOO000O000OOO0O0 .key ,'type':'xyyyd','val':'1','ven':oo0o }#line:171
            OO0O0O0O0000OO0OO =requests .get (OOO00O0000000OOO0 ,params =OO00O000O00O0O0OO ,timeout =5 )#line:172
            print (OOOO000O000OOO0O0 .name ,OO0O0O0O0000OO0OO .text )#line:173
            if '无效'in OO0O0O0O0000OO0OO .text :#line:174
                exit (0 )#line:175
        except Exception as O000OOOOOOO0O0OO0 :#line:176
            print (OOOO000O000OOO0O0 .name ,'设置状态异常')#line:177
            print (OOOO000O000OOO0O0 .name ,O000OOOOOOO0O0OO0 )#line:178
            return 99 #line:179
    def getstatus (OOO0O00OOOOOOO0OO ):#line:180
        try :#line:181
            O0O0000000OO0000O ='http://175.24.153.42:8882/getstatus'#line:182
            O0O0O0O0OOOO0OOO0 ={'key':OOO0O00OOOOOOO0OO .key ,'type':'xyyyd'}#line:183
            O0O00O0000OOOOO00 =requests .get (O0O0000000OO0000O ,params =O0O0O0O0OOOO0OOO0 ,timeout =3 )#line:184
            return O0O00O0000OOOOO00 .text #line:185
        except Exception as OO0O0OOO00O00O000 :#line:186
            print (OOO0O00OOOOOOO0OO .name ,'查询状态异常',OO0O0OOO00O00O000 )#line:187
            return False #line:188
    def getHost (OOOOOOOO0000OOO00 ):#line:189
        O0000O000O000OOO0 ='http://1727407399.onetmc.work/auth2/868cd99e0d7d5e0e034bd4f421c0587f?cate=0&self='#line:190
        OO0O000OO0OO0OOOO ={'Host':'1727407399.onetmc.work','Connection':'keep-alive','Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Linux; Android 13; M2104K10AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110017 MMWEBSDK/20231002 MMWEBID/2545 MicroMessenger/8.0.43.2480(0x28112BE1) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9','Cookie':f'ysmuid={OOOOOOOO0000OOO00.ysmuid}',}#line:200
        OOO0OOOO0OO00OOO0 =requests .get (O0000O000O000OOO0 ,headers =OO0O000OO0OO0OOOO ,allow_redirects =False )#line:201
        O0OO000O0O0O0000O =OOO0OOOO0OO00OOO0 .headers .get ('Location')#line:202
        O0OO000OO00OOO0OO =urlparse (O0OO000O0O0O0000O ).netloc #line:203
        OOOOOOOO0000OOO00 .getheaders0 ={'Host':O0OO000OO00OOO0OO ,'Connection':'keep-alive','Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Linux; Android 13; M2104K10AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110017 MMWEBSDK/20231002 MMWEBID/2545 MicroMessenger/8.0.43.2480(0x28112BE1) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9','Cookie':f'ysmuid={OOOOOOOO0000OOO00.ysmuid}; ejectCode=1',}#line:213
        OOOOOOOO0000OOO00 .getheaders ={'Host':O0OO000OO00OOO0OO ,'Connection':'keep-alive','Accept':'application/json, text/javascript, */*; q=0.01','User-Agent':'Mozilla/5.0 (Linux; Android 13; M2104K10AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110017 MMWEBSDK/20231002 MMWEBID/2545 MicroMessenger/8.0.43.2480(0x28112BE1) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64','X-Requested-With':'XMLHttpRequest','Referer':f'http://{O0OO000OO00OOO0OO}/?inviteid=0','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9','Cookie':f'ysmuid={OOOOOOOO0000OOO00.ysmuid}; ejectCode=1',}#line:224
        OOOOOOOO0000OOO00 .postheaders ={'Host':O0OO000OO00OOO0OO ,'Connection':'keep-alive','Accept':'application/json, text/javascript, */*; q=0.01','X-Requested-With':'XMLHttpRequest','User-Agent':'Mozilla/5.0 (Linux; Android 13; M2104K10AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110017 MMWEBSDK/20231002 MMWEBID/2545 MicroMessenger/8.0.43.2480(0x28112BE1) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','Origin':f'http://{O0OO000OO00OOO0OO}','Referer':f'http://{O0OO000OO00OOO0OO}/?inviteid=0','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9','Cookie':f'ysmuid={OOOOOOOO0000OOO00.ysmuid}; ejectCode=1',}#line:237
        OOOOOOOO0000OOO00 .mainurl =f'http://{O0OO000OO00OOO0OO}'#line:238
    def init (OO0OO00OOOO000OOO ):#line:239
        try :#line:240
            O0000O0OOO00OOOO0 =f'{OO0OO00OOOO000OOO.mainurl}/?inviteid=0'#line:241
            O0OOOOOO00O0O00O0 =requests .get (O0000O0OOO00OOOO0 ,headers =OO0OO00OOOO000OOO .getheaders0 )#line:242
            OO0O0O0O0O0O0O000 =O0OOOOOO00O0O00O0 .text #line:243
            OO00OOOOOO000000O =re .sub ('\s','',OO0O0O0O0O0O0O000 )#line:244
            O0OOO0O0000OOO00O =re .findall ("domain\+'(exchange.*?)'}",OO00OOOOOO000000O )#line:245
            O0000000O000O0O0O =re .findall ('{unionid="(.*?)"}',OO00OOOOOO000000O )#line:246
            if O0000000O000O0O0O ==[]:#line:247
                print (OO0OO00OOOO000OOO .name ,'初始化失败,账号异常,获取ysm_uid失败')#line:248
                return False #line:249
            else :#line:250
                OO0OO00OOOO000OOO .ysm_uid =O0000000O000O0O0O [0 ]#line:251
                if O0OOO0O0000OOO00O ==[]:#line:252
                    print (OO0OO00OOOO000OOO .name ,'初始化失败,账号异常，获取exchangeUrl失败')#line:253
                    return False #line:254
                else :#line:255
                    OO0OO00OOOO000OOO .eurl =O0OOO0O0000OOO00O [0 ]#line:256
                return True #line:257
        except :#line:258
            print (OO0OO00OOOO000OOO .name ,'初始化失败,请检查你的ck')#line:259
            return False #line:260
    def user_info (OOOO000OO00OO0O0O ):#line:262
        OOO000OO000O0OOOO =f'{OOOO000OO00OO0O0O.mainurl}/yunonline/v1/sign_info?time={ts()}000&unionid={OOOO000OO00OO0O0O.ysm_uid}'#line:263
        try :#line:264
            O0O00O00O00O00000 =requests .get (OOO000OO000O0OOOO ,headers =OOOO000OO00OO0O0O .getheaders )#line:265
            OO0OO0OOOO000O00O =O0O00O00O00O00000 .json ()#line:266
            if OO0OO0OOOO000O00O .get ('errcode')==0 :#line:267
                return True #line:268
            else :#line:269
                print (OOOO000OO00OO0O0O .name ,f'获取用户信息失败，账号异常，请查看你的账号是否正常')#line:270
                return False #line:271
        except :#line:272
            print (OOOO000OO00OO0O0O .name ,f'获取用户信息失败,ysmuid，请检测ysmuid是否正确')#line:273
            return False #line:274
    def hasWechat (OOOO0O0OOOO0OOOOO ):#line:276
        try :#line:277
            O00OO00O0OO0000OO =f'{OOOO0O0OOOO0OOOOO.mainurl}/yunonline/v1/hasWechat?unionid={OOOO0O0OOOO0OOOOO.ysm_uid}'#line:278
            O0OO0OO0OOOOO0O00 =requests .get (O00OO00O0OO0000OO ,headers =OOOO0O0OOOO0OOOOO .getheaders )#line:279
        except :#line:280
            print (OOOO0O0OOOO0OOOOO .name ,'异常hasWechat')#line:281
            return False #line:282
    def gold (OO00OOO0OOOO0O000 ):#line:284
        try :#line:285
            O00O0O0O0OO0OOO00 =f'{OO00OOO0OOOO0O000.mainurl}/yunonline/v1/gold?unionid={OO00OOO0OOOO0O000.ysm_uid}&time={ts()}000'#line:286
            OO0000O000OOO0O00 =requests .get (O00O0O0O0OO0OOO00 ,headers =OO00OOO0OOOO0O000 .getheaders )#line:287
            if 'success'in OO0000O000OOO0O00 .text :#line:288
                O00OO0OO00OOOO0O0 =OO0000O000OOO0O00 .json ()#line:289
                OO00OOO0OOOO0O000 .remain =O00OO0OO00OOOO0O0 .get ("data").get ("last_gold")#line:290
                print (OO00OOO0OOOO0O000 .name ,f'今日已经阅读了{O00OO0OO00OOOO0O0.get("data").get("day_read")}篇文章,剩余{O00OO0OO00OOOO0O0.get("data").get("remain_read")}未阅读，今日获取金币{O00OO0OO00OOOO0O0.get("data").get("day_gold")}，剩余{OO00OOO0OOOO0O000.remain}')#line:292
            else :#line:293
                print (OO0000O000OOO0O00 .text )#line:294
                return False #line:295
        except :#line:296
            print (OO00OOO0OOOO0O000 .name ,"异常gold")#line:297
            return False #line:298
    def getKey (O000OOOO0OOOOO00O ):#line:299
        O0OO0O0O00OOOO000 =f'{O000OOOO0OOOOO00O.mainurl}/wtmpdomain2'#line:300
        OO0OOO0000OO0OO0O =f'unionid={O000OOOO0OOOOO00O.ysm_uid}'#line:301
        O00OO00O000000000 =requests .post (O0OO0O0O00OOOO000 ,headers =O000OOOO0OOOOO00O .postheaders ,data =OO0OOO0000OO0OO0O )#line:302
        O00OO000O00OO000O =O00OO00O000000000 .json ()#line:303
        O0OOOO0OOO0OOO0OO =O00OO000O00OO000O .get ('data').get ('domain')#line:304
        OOO0OO0OOOO00OOO0 =parse_qs (urlparse (O0OOOO0OOO0OOO0OO ).query )#line:305
        O000OO0000O00O0OO =urlparse (O0OOOO0OOO0OOO0OO ).netloc #line:306
        O0O00O000O0000000 =OOO0OO0OOOO00OOO0 .get ('sy')[0 ]#line:307
        O0O0O000OOOO0000O ={'Host':O000OO0000O00O0OO ,'Connection':'keep-alive','Accept':'application/json, text/javascript, */*; q=0.01','User-Agent':'Mozilla/5.0 (Linux; Android 13; M2104K10AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110017 MMWEBSDK/20231002 MMWEBID/2545 MicroMessenger/8.0.43.2480(0x28112BE1) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64','X-Requested-With':'XMLHttpRequest','Referer':O0OOOO0OOO0OOO0OO ,'Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9',}#line:317
        return O0O00O000O0000000 ,O0O0O000OOOO0000O ,O000OO0000O00O0OO #line:318
    def read (O0O00O0000O000O00 ):#line:320
        OO0O0O0OO0O0O0OOO =O0O00O0000O000O00 .getKey ()#line:321
        time .sleep (2 )#line:322
        while True :#line:323
            O00000000O00O000O =int (ts ())#line:324
            O0OOOOO0O0OOO0OOO ={'sy':OO0O0O0OO0O0O0OOO [0 ],'psgn':'168','vs':'120','time':str (O00000000O00O000O )}#line:325
            OOOO0O0000O0O00OO =f'http://{OO0O0O0OO0O0O0OOO[2]}/teefreae6d2s'#line:326
            OOOO00O0O00OOO000 =requests .get (OOOO0O0000O0O00OO ,headers =OO0O0O0OO0O0O0OOO [1 ],params =O0OOOOO0O0OOO0OOO )#line:327
            print (O0O00O0000O000O00 .name ,'-'*50 )#line:328
            O000OOO000O00O0O0 =OOOO00O0O00OOO000 .json ()#line:329
            if O000OOO000O00O0O0 .get ('errcode')==0 :#line:330
                O000O0OO0O0OO000O =O000OOO000O00O0O0 .get ('data').get ('link')#line:331
                O000OO0OO0OOO0O0O =getinfo (O000O0OO0O0OO000O )#line:332
                if O0O00O0000O000O00 .testCheck (O000OO0OO0OOO0O0O ,O000O0OO0O0OO000O )==False :#line:333
                    return False #line:334
                O000O0000O00000OO =random .randint (8 ,13 )#line:335
                print (O0O00O0000O000O00 .name ,f'本次模拟读{O000O0000O00000OO}秒')#line:336
                time .sleep (O000O0000O00000OO )#line:337
                OOO0O0OO0000OOOOO =int (ts ())#line:338
                O00OO00O0OOOOOOOO =int ((OOO0O0OO0000OOOOO -O00000000O00O000O )/1000 )#line:339
                O0OOOOO0OO000O0O0 ={'sy':OO0O0O0OO0O0O0OOO [0 ],'time':O00OO00O0OOOOOOOO ,'timestamp':OOO0O0OO0000OOOOO }#line:340
                OO0O00OO0O00O0OOO =f'http://{OO0O0O0OO0O0O0OOO[2]}/jinbicp'#line:341
                O0OOOO0OO00O00000 =requests .get (OO0O00OO0O00O0OOO ,headers =OO0O0O0OO0O0O0OOO [1 ],params =O0OOOOO0OO000O0O0 )#line:342
                print (O0OOOO0OO00O00000 .json ())#line:343
            elif O000OOO000O00O0O0 .get ('errcode')==405 :#line:344
                print (O0O00O0000O000O00 .name ,'阅读重复')#line:345
                time .sleep (1.5 )#line:346
            elif O000OOO000O00O0O0 .get ('errcode')==407 :#line:347
                print (O0O00O0000O000O00 .name ,O000OOO000O00O0O0 .get ('msg'))#line:348
                print (O0O00O0000O000O00 .name ,'阅读结束')#line:349
                return True #line:350
            else :#line:351
                print (O0O00O0000O000O00 .name ,'未知情况')#line:352
                time .sleep (1.5 )#line:353
    def testCheck (O0OO0000OOO0OO00O ,OO00O000OO0OO0OO0 ,OOO0OOO0OOO0O0O0O ):#line:355
        if OO00O000OO0OO0OO0 [4 ]==[]:#line:356
            print (O0OO0000OOO0OO00O .name ,'这个链接没有获取到微信号id',OOO0OOO0OOO0O0O0O )#line:357
            return True #line:358
        if OO00O000OO0OO0OO0 [5 ]==[]:#line:359
            print (O0OO0000OOO0OO00O .name ,'这个链接没有获取到时间',OOO0OOO0OOO0O0O0O )#line:360
            return True #line:361
        if (checkDict .get (OO00O000OO0OO0OO0 [4 ])!=None )or (int (time .time ())-int (OO00O000OO0OO0OO0 [5 ])>3600 *24 *14 ):#line:362
            if O0OO0000OOO0OO00O .setstatus ()==99 :#line:363
                print (O0OO0000OOO0OO00O .name ,'过检测服务器异常，使用无回调方案，请在50s内阅读检测文章')#line:364
                push (f'小阅阅读过检测:{O0OO0000OOO0OO00O.name}',OOO0OOO0OOO0O0O0O ,OO00O000OO0OO0OO0 [3 ],'xyyyd',O0OO0000OOO0OO00O .uids ,O0OO0000OOO0OO00O .key )#line:365
                time .sleep (50 )#line:366
                return True #line:367
            for OOO0000OOOOO00OO0 in range (60 ):#line:368
                if OOO0000OOOOO00OO0 %30 ==0 :#line:369
                    O0O00OO00OO000O00 =f'http://175.24.153.42:8882/lookwxarticle?key=KEY&type=TYPE&wxurl={OOO0OOO0OOO0O0O0O}'#line:370
                    push (f'小阅阅阅读过检测:{O0OO0000OOO0OO00O.name}',O0O00OO00OO000O00 ,OO00O000OO0OO0OO0 [3 ],'xyyyd',O0OO0000OOO0OO00O .uids ,O0OO0000OOO0OO00O .key )#line:371
                OO0O0000O0O0000O0 =O0OO0000OOO0OO00O .getstatus ()#line:372
                if OO0O0000O0O0000O0 =='0':#line:373
                    print (O0OO0000OOO0OO00O .name ,'过检测文章已经阅读')#line:374
                    return True #line:375
                elif OO0O0000O0O0000O0 =='1':#line:376
                    print (O0OO0000OOO0OO00O .name ,f'正在等待过检测文章阅读结果{OOO0000OOOOO00OO0}秒。。。')#line:377
                    time .sleep (1 )#line:378
                else :#line:379
                    print (O0OO0000OOO0OO00O .name ,OO0O0000O0O0000O0 )#line:380
                    print (O0OO0000OOO0OO00O .name ,'服务器异常')#line:381
            print (O0OO0000OOO0OO00O .name ,'过检测超时中止脚本防止黑号')#line:382
            return False #line:383
        else :#line:384
            return True #line:385
    def withdraw (O00O000000O0O000O ):#line:387
        OOO0OO00OO00O000O =urlparse (O00O000000O0O000O .eurl )#line:388
        O0O000O0OOOO0O000 =parse_qs (OOO0OO00OO00O000O .query )#line:389
        O0O000O0OO0OO000O =O00O000000O0O000O .postheaders .copy ()#line:390
        O000OO0O00O00OO00 =urlparse (O00O000000O0O000O .mainurl ).netloc #line:391
        O0O000O0OO0OO000O .update ({'Referer':f'http://{O000OO0O00O00OO00}/yunonline/v1/{O00O000000O0O000O.eurl}'})#line:392
        if int (O00O000000O0O000O .remain )<3000 :#line:393
            print (O00O000000O0O000O .name ,'没有达到提现标准')#line:394
            return False #line:395
        O000OOO00OOOOOOO0 =int (int (O00O000000O0O000O .remain )/1000 )*1000 #line:396
        print (O00O000000O0O000O .name ,'本次提现金币',O000OOO00OOOOOOO0 )#line:397
        if O000OOO00OOOOOOO0 :#line:398
            O000O0O0000OO000O =O0O000O0OOOO0O000 .get ('unionid')[0 ]#line:399
            OO00O0OOO00O000O0 =O0O000O0OOOO0O000 .get ('request_id')[0 ]#line:400
            O00O000O00000OOOO =f'{O00O000000O0O000O.mainurl}/yunonline/v1/user_gold'#line:401
            O0O0OO000OO00O0O0 =f'unionid={O000O0O0000OO000O}&request_id={OO00O0OOO00O000O0}&gold={O000OOO00OOOOOOO0}'#line:402
            O00OO0O0O0OOOOOO0 =requests .post (O00O000O00000OOOO ,headers =O0O000O0OO0OO000O ,data =O0O0OO000OO00O0O0 ,)#line:403
            OOO0O000O0O00O00O =f'{O00O000000O0O000O.mainurl}/yunonline/v1/withdraw'#line:404
            O0OO000O0OOOO0OOO =f'unionid={O000O0O0000OO000O}&signid={OO00O0OOO00O000O0}&ua=0&ptype=0&paccount=&pname='#line:405
            O00OO0O0O0OOOOOO0 =requests .post (OOO0O000O0O00O00O ,headers =O0O000O0OO0OO000O ,data =O0OO000O0OOOO0OOO ,)#line:406
            print (O00O000000O0O000O .name ,'提现结果',O00OO0O0O0OOOOOO0 .json ())#line:407
    def run (OOO00O0O00000O0O0 ):#line:409
        if hashlib .md5 (oo0o .encode ()).hexdigest ()!='ab18f35abad399de44af400c6e0c6dcf':OOO00O0O00000O0O0 .setstatus ()#line:410
        OOO00O0O00000O0O0 .getHost ()#line:411
        if OOO00O0O00000O0O0 .init ():#line:412
            OOO00O0O00000O0O0 .user_info ()#line:413
            OOO00O0O00000O0O0 .hasWechat ()#line:414
            OOO00O0O00000O0O0 .gold ()#line:415
            time .sleep (3 )#line:416
            OOO00O0O00000O0O0 .read ()#line:417
            time .sleep (3 )#line:418
            OOO00O0O00000O0O0 .gold ()#line:419
            time .sleep (3 )#line:420
            OOO00O0O00000O0O0 .withdraw ()#line:421
def getEnv (O000OOO000O0OO00O ):#line:423
    OO0000OOOO0O00000 =os .getenv (O000OOO000O0OO00O )#line:424
    if OO0000OOOO0O00000 ==None :#line:425
        print (f'{O000OOO000O0OO00O}青龙变量里没有获取到')#line:426
        exit (0 )#line:427
    try :#line:428
        OO0000OOOO0O00000 =json .loads (OO0000OOOO0O00000 .replace ("'",'"').replace ("\n","").replace (" ","").replace ("\t",""))#line:429
        return OO0000OOOO0O00000 #line:430
    except Exception as OOO00O00000OOO000 :#line:431
        print ('错误:',OOO00O00000OOO000 )#line:432
        print ('你填写的变量是:',OO0000OOOO0O00000 )#line:433
        print ('请检查变量参数是否填写正确')#line:434
if __name__ =='__main__':#line:435
    pushconfig =getEnv ('push_config')#line:436
    xyyconfig =getEnv ('xyyconfig')#line:437
    printf =pushconfig ['printf']#line:439
    appToken =pushconfig ['appToken']#line:440
    threadingf =pushconfig ['threadingf']#line:441
    getmsg ()#line:442
    tl =[]#line:443
    if threadingf ==1 :#line:444
        for cg in xyyconfig :#line:445
            print (f'开始执行{cg["name"]}')#line:446
            api =HHYD (cg )#line:447
            t =threading .Thread (target =api .run ,args =())#line:448
            tl .append (t )#line:449
            t .start ()#line:450
            time .sleep (0.5 )#line:451
        for t in tl :#line:452
            t .join ()#line:453
    elif threadingf ==0 :#line:454
        for cg in xyyconfig :#line:455
            print ('*'*50 )#line:456
            print (f'开始执行{cg["name"]}')#line:457
            api =HHYD (cg )#line:458
            api .run ()#line:459
            print (f'{cg["name"]}执行完毕')#line:460
            time .sleep (3 )#line:461
    else :#line:462
        print ('请确定推送变量中threadingf参数是否正确')#line:463
    print ('全部账号执行完成')#line:464
