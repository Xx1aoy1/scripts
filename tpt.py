import time #line:5
import os #line:6
import random #line:7
import requests #line:8
import datetime #line:9
ck =os .environ .get ("tptck")#line:11
kqid =66 #line:13
class TPT :#line:15
    def __init__ (OOOO0OO000OOOOO0O ):#line:16
        OOOO0OO000OOOOO0O .accounts_list =ck .strip ().split ('\n')#line:17
        OOOO0OO000OOOOO0O .num_of_accounts =len (OOOO0OO000OOOOO0O .accounts_list )#line:18
        print (f'NONE益达,共找到{OOOO0OO000OOOOO0O.num_of_accounts}个账号,开始运行\n')#line:19
    def run (OO000000O000OOO0O ):#line:21
        for OO0O000OO0OOOOOO0 ,OO0O0O000000OO0OO in enumerate (OO000000O000OOO0O .accounts_list ,start =1 ):#line:22
            try :#line:23
              OO00O0OOO00OO0OO0 ,O0O0O000OOOOOO000 =OO0O0O000000OO0OO .split ('&')#line:24
            except ValueError :#line:25
                print ("输入数据格式不正确，请检查输入并重新尝试。")#line:26
            OO000000O000OOO0O .headers ={'Host':'ecustomer.cntaiping.com','Accept':'application/json;charset=UTF-8','x-ac-token-ticket':O0O0O000OOOOOO000 ,'x-ac-channel-id':'KHT','Accept-Language':'zh-cn','Accept-Encoding':'gzip, deflate, br','Content-Type':'application/json','Origin':'https://ecustomercdn.itaiping.com','Content-Length':'39','User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/77777;yuangongejia#ios#kehutong#CZBIOS','Referer':'https://ecustomercdn.itaiping.com/','x-ac-mc-type':'gateway.user','Connection':'keep-alive'}#line:43
            OO000000O000OOO0O ._headers ={'Host':'ecustomer.cntaiping.com','Accept':'application/json, text/plain, */*','API-TOKEN':O0O0O000OOOOOO000 ,'Accept-Language':'zh-cn','Content-Type':'application/json;charset=utf-8','Origin':'https://ecustomercdn.itaiping.com','User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/77777;yuangongejia#ios#kehutong#CZBIOS','Connection':'keep-alive','Referer':'https://ecustomercdn.itaiping.com/','ENV':'app',}#line:55
            print (f"==============开始执行账号{OO0O000OO0OOOOOO0}==============")#line:56
            if OO000000O000OOO0O .login (OO00O0OOO00OO0OO0 ,O0O0O000OOOOOO000 ):#line:57
                OO000000O000OOO0O .process_account (OO00O0OOO00OO0OO0 ,O0O0O000OOOOOO000 )#line:58
                print (f"==============运行结束==============")#line:59
    def login (OO0O000O00OO0000O ,OO000O00OO00O00OO ,OOO0OOOOO0OO0OO0O ):#line:61
        O0000O000O00000OO ="https://ecustomer.cntaiping.com/campaignsms/integral/queryIntegralDetailList"#line:62
        OO00O00O0OO0O0OO0 ={'pageNo':1 ,'pageSize':10 ,'typePo':'3',}#line:67
        OOO00OO0OO00O0000 =requests .post (O0000O000O00000OO ,headers =OO0O000O00OO0000O .headers ,json =OO00O00O0OO0O0OO0 )#line:68
        OO0OOOO0OO0000OOO =OOO00OO0OO00O0000 .json ()#line:69
        if OO0OOOO0OO0000OOO ['success']==True :#line:71
            print (f"{OO000O00OO00O00OO}: 登录成功")#line:72
            time .sleep (2 )#line:73
            O0OO0O0O000O0OO0O =OO0OOOO0OO0000OOO ['data']['list']#line:74
            if O0OO0O0O000O0OO0O is not None :#line:75
                for OOOO00OO0OO0000O0 in O0OO0O0O000O0OO0O :#line:76
                    OO0OOOOO0O0OO00OO =OOOO00OO0OO0000O0 ['effectDate']#line:77
                    O00O0O0OOOOO0000O =OOOO00OO0OO0000O0 ['memo']#line:78
                    OO0OOO000O00OO0OO =OOOO00OO0OO0000O0 ['overDate']#line:79
                    OOOO0000O00O0O00O =OOOO00OO0OO0000O0 ['num']#line:80
                    OOOOOO0O00O00OO00 =OOOO00OO0OO0000O0 ['createTime']#line:81
                    print (f"{O00O0O0OOOOO0000O}[{OOOO0000O00O0O00O}]-有效期[{OOOOOO0O00O00OO00}]")#line:82
            return True #line:83
        else :#line:84
            print (f"{OO000O00OO00O00OO}: 登录失败,{OO0OOOO0OO0000OOO['msg']}")#line:85
            return False #line:86
    def process_account (O0O000000O00OOO00 ,OO0OO0O0OO0OO000O ,OOO0OOO0O00O0OOOO ):#line:88
        OO0O00OO000OOO0O0 ="https://ecustomer.cntaiping.com/campaignsms/couponAndsign"#line:89
        _OO00O00O0O0OOO0O0 ={}#line:90
        print (f"==============每日签到==============")#line:91
        OO0OOOO0OO0O0OOO0 =requests .post (OO0O00OO000OOO0O0 ,headers =O0O000000O00OOO00 .headers ,json =_OO00O00O0O0OOO0O0 )#line:92
        OOO000O0O00000O0O =OO0OOOO0OO0O0OOO0 .json ()#line:94
        if OOO000O0O00000O0O ['success']==True :#line:95
            OOO0OOOO0O0000OO0 =OOO000O0O00000O0O ['data']['dailySignRsp']['message']#line:96
            O0O0000OOO0O0OO00 =OOO000O0O00000O0O ['data']['dailySignRsp']['integralSend']#line:97
            O0O000000O00OOO00 .integral =OOO000O0O00000O0O ['data']['dailySignRsp']['integral']#line:98
            print (f"签到-{OOO0OOOO0O0000OO0}[{O0O0000OOO0O0OO00}]-当前有{O0O000000O00OOO00.integral}金币")#line:99
        else :#line:100
            print (f"签到失败,{OOO000O0O00000O0O['msg']}")#line:101
        O0000OO000OO0O0OO ="https://ecustomer.cntaiping.com/campaignsms/goldParty/task/list"#line:102
        _OOO000000O0O0O0OO ={'activityNumber':'goldCoinParty','rewardFlag':'1','openMsgRemind':0 ,}#line:107
        print (f"==============日常任务==============")#line:108
        OO0OOOO0OO0O0OOO0 =requests .post (O0000OO000OO0O0OO ,headers =O0O000000O00OOO00 .headers ,json =_OOO000000O0O0O0OO )#line:109
        OOO0OO0O0000O000O =OO0OOOO0OO0O0OOO0 .json ()#line:110
        if OOO0OO0O0000O000O ['success']==True :#line:111
            OOOOOO0O00OO0O0O0 =OOO0OO0O0000O000O ['data']['taskList']#line:112
            for OO0O0000OOOO0OOO0 in OOOOOO0O00OO0O0O0 :#line:113
                _OO00OO0OOOO00O000 =OO0O0000OOOO0OOO0 ['taskId']#line:114
                _O0000O0O0OO00O0OO =OO0O0000OOOO0OOO0 ['name']#line:115
                time .sleep (4 )#line:116
                print (f"去完成{_O0000O0O0OO00O0OO}任务")#line:117
                O00O00O00O00O0OO0 ="https://ecustomer.cntaiping.com/campaignsms/goldParty/task/finish"#line:118
                _O0O00000OOOO0OO00 ={'taskIds':[_OO00OO0OOOO00O000 ,],}#line:123
                OO0OOOO0OO0O0OOO0 =requests .post (O00O00O00O00O0OO0 ,headers =O0O000000O00OOO00 .headers ,json =_O0O00000OOOO0OO00 )#line:124
                OOO0O00O0OOOOO00O =OO0OOOO0OO0O0OOO0 .json ()#line:125
                if OOO0O00O0OOOOO00O ['success']==True :#line:127
                    print (f"完成{_O0000O0O0OO00O0OO}任务成功")#line:128
                else :#line:129
                    print (f"完成{_O0000O0O0OO00O0OO}任务失败,{OOO0O00O0OOOOO00O['msg']}")#line:130
                time .sleep (3 )#line:131
                O00000O00O0OOO0O0 ="https://ecustomer.cntaiping.com/campaignsms/goldParty/goldCoin/add"#line:132
                _O0O0OO0O00OO0OO0O ={'taskIds':[_OO00OO0OOOO00O000 ,],}#line:137
                OO0OOOO0OO0O0OOO0 =requests .post (O00000O00O0OOO0O0 ,headers =O0O000000O00OOO00 .headers ,json =_O0O0OO0O00OO0OO0O )#line:138
                OO00000OOO00000O0 =OO0OOOO0OO0O0OOO0 .json ()#line:139
                if OO00000OOO00000O0 ['success']==True :#line:141
                    print (f"领取{_O0000O0O0OO00O0OO}任务奖励成功")#line:142
                else :#line:143
                    print (f"领取{_O0000O0O0OO00O0OO}任务奖励失败,{OO00000OOO00000O0['msg']}")#line:144
        else :#line:145
            print (f"获取任务失败,{OO0O0000OOOO0OOO0['msg']}")#line:146
        O0OOOOO0OO00O000O ="https://ecustomer.cntaiping.com/informationms/app/config/get/1"#line:147
        _O00OOOO000O000OO0 ={"plugInId":"701b3099297148a8ba979ad9c982b561","trackDesc":"赚金币任务","city":"1","pageSize":10 ,"type":"GENERAL_PLUGIN"}#line:154
        print (f"==============日常阅读==============")#line:155
        OO0OOOO0OO0O0OOO0 =requests .post (O0OOOOO0OO00O000O ,headers =O0O000000O00OOO00 .headers ,json =_O00OOOO000O000OO0 )#line:156
        O00O0O0000O000OOO =OO0OOOO0OO0O0OOO0 .json ()#line:157
        if O00O0O0000O000OOO ['success']==True :#line:158
            OO00O0O00000O00O0 =O00O0O0000O000OOO ['data']#line:159
            for O0O0OO000000OOOO0 in OO00O0O00000O00O0 :#line:160
                O0O0000O0OO0O0O00 =O0O0OO000000OOOO0 ['cell']['0'][0 ]#line:161
                _O000O0OOO00000O0O =O0O0000O0OO0O0O00 ['title']#line:162
                _O0O0OOO00O0O00OOO =O0O0000O0OO0O0O00 ['contentId']#line:163
                print (f"去阅读[{_O000O0OOO00000O0O}]")#line:164
                O0O000000O00OOO00 .l =random .uniform (5 ,6 )#line:165
                time .sleep (O0O000000O00OOO00 .l )#line:166
                O00OOO00O0OO0OOO0 ="https://ecustomer.cntaiping.com/informationms/app/v2/article/web/coinInfoV2"#line:167
                _OOOOO000OOOOO000O ={'articleId':_O0O0OOO00O0O00OOO ,'source':'TPT','detailUrl':f'https://ecustomercdn.itaiping.com/static/newscontent/#/info?articleId={_O0O0OOO00O0O00OOO}&source=TPT&x_utmId=10013&x_businesskey=articleId','deviceId':'','version':'V2',}#line:174
                OO0OOOO0OO0O0OOO0 =requests .post (O00OOO00O0OO0OOO0 ,headers =O0O000000O00OOO00 .headers ,json =_OOOOO000OOOOO000O )#line:175
                O0O000000OO0OOOO0 =OO0OOOO0OO0O0OOO0 .json ()#line:176
                if O0O000000OO0OOOO0 ['success']==True :#line:177
                    O0O000000O00OOO00 .p =O0O000000OO0OOOO0 ['data']['countDownCoinInfo']['coinNum']#line:178
                    pass #line:180
                else :#line:181
                    print (f"进入阅读[{_O000O0OOO00000O0O}奖励失败,{p['msg']}]")#line:182
                time .sleep (O0O000000O00OOO00 .l )#line:183
                O0O00OO00000OOOO0 ="https://ecustomer.cntaiping.com/informationms/app/v2/read/gold"#line:184
                _O000O0O0O0O0OOOOO ={"articleId":_O0O0OOO00O0O00OOO ,"source":"TPT"}#line:188
                OO0OOOO0OO0O0OOO0 =requests .post (O0O00OO00000OOOO0 ,headers =O0O000000O00OOO00 .headers ,json =_O000O0O0O0O0OOOOO )#line:189
                O00O0OOOOO0O0000O =OO0OOOO0OO0O0OOO0 .json ()#line:190
                if O00O0OOOOO0O0000O ['success']==True :#line:191
                    O0O0OOO00O0O000O0 =O00O0OOOOO0O0000O ['data']['coinTrackDto']['title']#line:192
                    print (f"阅读[{O0O0OOO00O0O000O0}]成功获得{O0O000000O00OOO00.p}金币")#line:193
                else :#line:194
                    print (f"阅读[{_O000O0OOO00000O0O}失败,{O00O0OOOOO0O0000O['msg']}]")#line:195
        else :#line:196
            print (f"阅读[{_O000O0OOO00000O0O}]失败,{O00O0O0000O000OOO['msg']}")#line:197
        O000OOOOO000O0OOO ="https://ecustomer.cntaiping.com/campaignsms/coinBubble/getAllCoins"#line:198
        _O0O000OOOO00OOO0O ={}#line:199
        print (f"==============领取阅读奖励==============")#line:200
        OO0OOOO0OO0O0OOO0 =requests .post (O000OOOOO000O0OOO ,headers =O0O000000O00OOO00 .headers ,json =_O0O000OOOO00OOO0O )#line:201
        O00O0OOOO0O000O0O =OO0OOOO0OO0O0OOO0 .json ()#line:202
        if O00O0OOOO0O000O0O ['success']==True :#line:204
            O00000O0OOO0OOOOO =O00O0OOOO0O000O0O ['data']['coinNum']#line:205
            print (f"领取阅读奖励-{O00000O0OOO0OOOOO}金币")#line:206
        else :#line:207
            print (f"领取阅读奖励失败,{O00O0OOOO0O000O0O['msg']}")#line:208
        print (f"==============兑换卡券==============")#line:209
        O00OOO00O0OO0OOO0 ="https://ecustomer.cntaiping.com/campaignsms/coin/exchange/receive"#line:210
        _OOOOO000OOOOO000O ={'id':kqid ,}#line:213
        OO0OOOO0OO0O0OOO0 =requests .post (O00OOO00O0OO0OOO0 ,headers =O0O000000O00OOO00 .headers ,json =_OOOOO000OOOOO000O )#line:214
        O0O000000OO0OOOO0 =OO0OOOO0OO0O0OOO0 .json ()#line:215
        if O0O000000OO0OOOO0 ['success']==True :#line:217
            O0O00O00OOO00O0OO =O0O000000OO0OOOO0 ['data']['couponId']#line:218
            print (f"卡券兑换成功-{O0O00O00OOO00O0OO}")#line:219
        else :#line:220
            print (f"卡券兑换失败,{O0O000000OO0OOOO0['msg']}")#line:221
        print (f"==============水滴浇树==============")#line:222
        OO000O000O00000OO ="https://ecustomer.cntaiping.com/love-tree/v2/api/task/complete-newcomer-water"#line:224
        _O0O000OOOOO00OO0O ={"tid":1 }#line:227
        OO0OOOO0OO0O0OOO0 =requests .post (OO000O000O00000OO ,headers =O0O000000O00OOO00 ._headers ,json =_O0O000OOOOO00OO0O )#line:228
        OO000OO000O0O00O0 =OO0OOOO0OO0O0OOO0 .json ()#line:229
        if OO000OO000O0O00O0 ['code']==200 :#line:231
            O0O0OO0O00000OO0O =OO000OO000O0O00O0 ['data']['water']#line:232
            print (f"完成新人奖励成功,获得了{O0O0OO0O00000OO0O}水滴")#line:233
        else :#line:234
            print (f"完成新人奖励失败,{OO000OO000O0O00O0['msg']}")#line:235
        time .sleep (2 )#line:237
        O0O00O0OOO00OO0O0 ="https://ecustomer.cntaiping.com/love-tree/v2/api/task/complete-task"#line:238
        _O0O0O0O000O00O000 ={"type":14 }#line:241
        OO0OOOO0OO0O0OOO0 =requests .post (O0O00O0OOO00OO0O0 ,headers =O0O000000O00OOO00 ._headers ,json =_O0O0O0O000O00O000 )#line:242
        O00O0O0000O000OOO =OO0OOOO0OO0O0OOO0 .json ()#line:243
        if O00O0O0000O000OOO ['code']==200 :#line:245
            O0O0OO0O00000OO0O =O00O0O0000O000OOO ['data']['water']#line:246
            print (f"完成每月登录奖励成功,获得了{O0O0OO0O00000OO0O}水滴")#line:247
        else :#line:248
            print (f"完成每月登录奖励失败,{O00O0O0000O000OOO['msg']}")#line:249
        time .sleep (2 )#line:251
        OOOO0OOO0O0OOO0OO ="https://ecustomer.cntaiping.com/love-tree/v2/api/task/complete-link-task"#line:252
        _O00OOOOOO00000OOO ={"tid":15 }#line:255
        OO0OOOO0OO0O0OOO0 =requests .post (OOOO0OOO0O0OOO0OO ,headers =O0O000000O00OOO00 ._headers ,json =_O00OOOOOO00000OOO )#line:256
        OOOOOO0O00OO0O0O0 =OO0OOOO0OO0O0OOO0 .json ()#line:257
        if OOOOOO0O00OO0O0O0 ['code']==200 :#line:259
            O0O0OO0O00000OO0O =OOOOOO0O00OO0O0O0 ['data']['water']#line:260
            print (f"完成查保单领水滴奖励成功,获得了{O0O0OO0O00000OO0O}水滴")#line:261
        else :#line:262
            print (f"完成查保单领水滴奖励失败,{OOOOOO0O00OO0O0O0['msg']}")#line:263
        time .sleep (2 )#line:265
        O00000O0O0O000OO0 ="https://ecustomer.cntaiping.com/love-tree/v2/api/task/complete-red-envelope"#line:266
        _OOO000000O000OO00 ={"tid":3 }#line:269
        OO0OOOO0OO0O0OOO0 =requests .post (O00000O0O0O000OO0 ,headers =O0O000000O00OOO00 ._headers ,json =_OOO000000O000OO00 )#line:270
        OOO000O0O00000O0O =OO0OOOO0OO0O0OOO0 .json ()#line:271
        if OOO000O0O00000O0O ['code']==200 :#line:273
            O0O0OO0O00000OO0O =OOO000O0O00000O0O ['data']['water']#line:274
            print (f"完成三餐福袋奖励成功,获得了{O0O0OO0O00000OO0O}水滴")#line:275
        else :#line:276
            print (f"完成三餐福袋奖励失败,{OOO000O0O00000O0O['msg']}")#line:277
        for O0O00OOOO00O00O00 in range (6 ):#line:281
            time .sleep (2 )#line:282
            OO000000O0O0OOOO0 ="https://ecustomer.cntaiping.com/userms/serviceAccount/queryAllServiceAccount/v1"#line:283
            _OO0O0000000O0OO00 ={"pageSize":"15","page":"1"}#line:287
            OO0OOOO0OO0O0OOO0 =requests .post (OO000000O0O0OOOO0 ,headers =O0O000000O00OOO00 ._headers ,json =_OO0O0000000O0OO00 )#line:288
            OOO0O00O0OOOOO00O =OO0OOOO0OO0O0OOO0 .json ()#line:289
            if OOO0O00O0OOOOO00O ['success']==True :#line:291
                O0O000000O00OOO00 .wzid =random .choice (OOO0O00O0OOOOO00O ['data']['contents'])['id']#line:293
                print (f"随机获取关注ID成功[{O0O000000O00OOO00.wzid}]")#line:294
                time .sleep (2 )#line:295
                OOOOOOO00O0000O00 ="https://ecustomer.cntaiping.com/userms/serviceAccount/subscribe"#line:296
                _OO00O000O00O0OO00 ={"serviceAccountId":O0O000000O00OOO00 .wzid }#line:299
                OO0OOOO0OO0O0OOO0 =requests .post (OOOOOOO00O0000O00 ,headers =O0O000000O00OOO00 .headers ,json =_OO00O000O00O0OO00 )#line:300
                OOOOOOO0OOOOOO00O =OO0OOOO0OO0O0OOO0 .json ()#line:301
                if OOOOOOO0OOOOOO00O ['success']==True :#line:303
                   pass #line:304
                else :#line:305
                    print (f"关注文章失败,{OOOOOOO0OOOOOO00O['msg']}")#line:306
                    break #line:307
                time .sleep (2 )#line:308
                OOOOOO0O000OOOOO0 ="https://ecustomer.cntaiping.com/love-tree/v2/api/task/get-task-result"#line:309
                _OO0OO0O0O0OO0O00O ={}#line:310
                OO0OOOO0OO0O0OOO0 =requests .post (OOOOOO0O000OOOOO0 ,headers =O0O000000O00OOO00 ._headers ,json =_OO0OO0O0O0OO0O00O )#line:311
                O0OO00OOOOOOOO00O =OO0OOOO0OO0O0OOO0 .json ()#line:312
                if O0OO00OOOOOOOO00O ['code']==200 :#line:314
                    O0000O0O0OO0O000O =O0OO00OOOOOOOO00O ['data']#line:315
                    if O0OO00OOOOOOOO00O ['data']and len (O0OO00OOOOOOOO00O ['data'])>0 :#line:316
                        O0O0OO0O00000OO0O =O0OO00OOOOOOOO00O ['data'][0 ]['water']#line:317
                        print (f"完成关注太平通服务号成功获得了{O0O0OO0O00000OO0O}水滴")#line:318
                    else :#line:319
                        print (f"完成关注太平通服务号未获得水滴")#line:320
                else :#line:322
                    print (f"完成关注太平通服务号失败,{O0OO00OOOOOOOO00O['msg']}")#line:323
                    break #line:324
            else :#line:325
                print (f"获取文章ID失败,{OOO0O00O0OOOOO00O['msg']}")#line:326
                break #line:327
        time .sleep (2 )#line:329
        OO0O0O0O0OOO00OOO ="https://ecustomer.cntaiping.com/informationms/app/config/get/1"#line:330
        _OO0O0OOO000O0O0OO ={"plugInId":"701b3099297148a8ba979ad9c982b561","trackDesc":"赚金币任务","city":"1","pageSize":10 ,"type":"GENERAL_PLUGIN"}#line:337
        OO0OOOO0OO0O0OOO0 =requests .post (OO0O0O0O0OOO00OOO ,headers =O0O000000O00OOO00 ._headers ,json =_OO0O0OOO000O0O0OO )#line:338
        O0O000000OO0OOOO0 =OO0OOOO0OO0O0OOO0 .json ()#line:339
        if O0O000000OO0OOOO0 ['success']==True :#line:341
            OOO0O0000OO0OOO00 =O0O000000OO0OOOO0 ['data']#line:342
            for O0O0OO000000OOOO0 in OOO0O0000OO0OOO00 :#line:343
                _OOOOOOO00O0O0O00O =O0O0OO000000OOOO0 ['cell']['0'][0 ]#line:344
                _OO0O0OOO0OOOO00O0 =_OOOOOOO00O0O0O00O ['serviceNo']#line:345
                OOO0OO00O0O00000O =_OOOOOOO00O0O0O00O ['contentId']#line:346
                print (f"文章ID成功[{_OO0O0OOO0OOOO00O0}]-[{OOO0OO00O0O00000O}]")#line:347
                time .sleep (2 )#line:349
                OO000000O0O0OOOO0 ="https://ecustomer.cntaiping.com/informationms/app/v2/article/web/coinInfoV2"#line:350
                _OO0O0000000O0OO00 ={"detailUrl":f'https://ecustomercdn.itaiping.com/static/newscontent/#/info?articleId={OOO0OO00O0O00000O}&source=TPT&x_utmId=10013&x_businesskey=articleId',"deviceId":"","version":"V2","source":"TPT","articleId":OOO0OO00O0O00000O }#line:357
                OO0OOOO0OO0O0OOO0 =requests .post (OO000000O0O0OOOO0 ,headers =O0O000000O00OOO00 .headers ,json =_OO0O0000000O0OO00 )#line:358
                OOO0O00O0OOOOO00O =OO0OOOO0OO0O0OOO0 .json ()#line:359
                if OOO0O00O0OOOOO00O ['success']==True :#line:361
                    pass #line:362
                else :#line:363
                    print (f"阅一读文章失败,{OOO0O00O0OOOOO00O['msg']}")#line:364
                time .sleep (2 )#line:366
                OO0OO000000OO00O0 ="https://ecustomer.cntaiping.com/userms/serviceAccount/queryBasic"#line:367
                _OO00000OO0OOOOOO0 ={"id":_OO0O0OOO0OOOO00O0 }#line:370
                OO0OOOO0OO0O0OOO0 =requests .post (OO0OO000000OO00O0 ,headers =O0O000000O00OOO00 .headers ,json =_OO00000OO0OOOOOO0 )#line:371
                OO00O0O00000O00O0 =OO0OOOO0OO0O0OOO0 .json ()#line:372
                if OO00O0O00000O00O0 ['success']==True :#line:374
                    pass #line:375
                else :#line:376
                    print (f"阅二读文章失败,{OO00O0O00000O00O0['msg']}")#line:377
                time .sleep (2 )#line:379
                O0OO00O0O00OOO00O ="https://ecustomer.cntaiping.com/informationms/app/v2/read/gold"#line:380
                _OO00O000O0OOO0OO0 ={"articleId":OOO0OO00O0O00000O ,"source":"TPT"}#line:384
                OO0OOOO0OO0O0OOO0 =requests .post (O0OO00O0O00OOO00O ,headers =O0O000000O00OOO00 .headers ,json =_OO00O000O0OOO0OO0 )#line:385
                OO0OOO0OOO0O00O0O =OO0OOOO0OO0O0OOO0 .json ()#line:386
                if OO0OOO0OOO0O00O0O ['success']==True :#line:388
                    O0O000000O00OOO00 .LL =OO0OOO0OOO0O00O0O ['data']['coinTrackDto']['title']#line:389
                    print (f"阅三读[{O0O000000O00OOO00.LL}]成功")#line:390
                else :#line:391
                    print (f"阅读文章失败,{OO0OOO0OOO0O00O0O['msg']}")#line:392
                    break #line:393
                time .sleep (2 )#line:394
                O000000OOOOO0O00O ="https://ecustomer.cntaiping.com/love-tree/v2/api/task/get-task-result"#line:395
                _O0O0OOOOO000000O0 ={}#line:396
                OO0OOOO0OO0O0OOO0 =requests .post (O000000OOOOO0O00O ,headers =O0O000000O00OOO00 ._headers ,json =_O0O0OOOOO000000O0 )#line:397
                OO0O0000OOOO0OOO0 =OO0OOOO0OO0O0OOO0 .json ()#line:398
                print (OO0OOOO0OO0O0OOO0 .text )#line:399
                if OO0O0000OOOO0OOO0 ['data']and len (OO0O0000OOOO0OOO0 ['data'])>0 :#line:401
                    O0O0OO0O00000OO0O =OO0O0000OOOO0OOO0 ['data'][0 ]['water']#line:402
                    print (f"完成阅读{O0O000000O00OOO00.LL}成功获得了{O0O0OO0O00000OO0O}水滴")#line:403
                else :#line:404
                    print (f"完成阅读[{O0O000000O00OOO00.LL}]未获得水滴")#line:405
        else :#line:407
            print (f"获取阅读文章ID失败,{O0O000000OO0OOOO0['msg']}")#line:408
        O0OO00O0O00OOO00O ="https://ecustomer.cntaiping.com/love-tree/v2/api/user/open-welfare_box"#line:410
        _OO00O000O0OOO0OO0 ={"tree_user_id":256533 }#line:413
        OO0OOOO0OO0O0OOO0 =requests .post (O0OO00O0O00OOO00O ,headers =O0O000000O00OOO00 ._headers ,json =_OO00O000O0OOO0OO0 )#line:414
        OO0OOO0OOO0O00O0O =OO0OOOO0OO0O0OOO0 .json ()#line:415
        if OO0OOO0OOO0O00O0O ['code']==200 :#line:417
            O0OO0O0O00O0O00OO =OO000OO000O0O00O0 ['data']['water']#line:418
            print (f"领取神秘宝箱成功！获得了{O0OO0O0O00O0O00OO}水滴")#line:419
        else :#line:420
            print (f"领取神秘宝箱失败,{OO0OOO0OOO0O00O0O['msg']}")#line:421
        OO000O000O00000OO ="https://ecustomer.cntaiping.com/love-tree/v2/api/user/home"#line:423
        print (f"==============查询水滴==============")#line:424
        OO0OOOO0OO0O0OOO0 =requests .get (OO000O000O00000OO ,headers =O0O000000O00OOO00 ._headers )#line:425
        OO000OO000O0O00O0 =OO0OOOO0OO0O0OOO0 .json ()#line:426
        if OO000OO000O0O00O0 ['code']==200 :#line:428
            OOO0000O00O0O0OO0 =OO000OO000O0O00O0 ['data']['water']#line:429
            O0OOO0OO0OO0O00O0 =OOO0000O00O0O0OO0 //50 #line:430
            print (f"查询当前有{OOO0000O00O0O0OO0}水滴可以浇水{O0OOO0OO0OO0O00O0}次")#line:431
            for O0O00OOOO00O00O00 in range (O0OOO0OO0OO0O00O0 ):#line:432
               time .sleep (2 )#line:433
               OOOO0000OOOO00O0O ="https://ecustomer.cntaiping.com/love-tree/v2/api/tree/watering"#line:434
               _OO00OOOO000O0OOO0 ={"tree_user_id":256533 }#line:437
               OO0OOOO0OO0O0OOO0 =requests .post (OOOO0000OOOO00O0O ,headers =O0O000000O00OOO00 ._headers ,json =_OO00OOOO000O0OOO0 )#line:438
               O00O0OOOOO0O0000O =OO0OOOO0OO0O0OOO0 .json ()#line:439
               if O00O0OOOOO0O0000O ['code']==200 :#line:440
                   O0O0O00O0O00OO0O0 =O00O0OOOOO0O0000O ['data']['sy_water']#line:441
                   print (f"浇水成功！还剩余{O0O0O00O0O00OO0O0}水滴")#line:442
               else :#line:443
                   print (f"浇水失败,{O00O0OOOOO0O0000O['msg']}")#line:444
        else :#line:445
            print (f"查询水滴失败,{OO000OO000O0O00O0['msg']}")#line:446
tpt =TPT ()#line:447
tpt .run ()
