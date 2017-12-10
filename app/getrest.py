# encoding=utf-8
import requests
import re


# url = "http://www.ccb.com/tran/WCCMainPlatV5" 获取header


def getHeaders(url):
    querystring = {"CCB_IBSVersion":"V5","SERVLET_NAME":"WCCMainPlatV5","TXCODE":"NYS10Z","DCRINDEX":"201509260725204147","BILL_TYPE":"500","BILL_ITEM":"05013"}

    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9",
        'connection': "keep-alive",
        'cookie': "BIGipServerccvcc_jt_10.3.198.1_tcp80_web_pool=1361249034.20480.0000",
        'host': "www.ccb.com",
        'referer': "http://www.ccb.com/cn/paymentv3/bill_item/201509260725204147.html",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        'cache-control': "no-cache",
        'postman-token': "36e3718d-8d4c-3da6-a90a-08f5f47b53a0"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return {
        'cookie':response.headers.get('Set-Cookie'),
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",

    }




def getRest(id,headers):
    d1 = 'BANK_COD=360000&BUTTON_IMG=&BUTTON_URL=&OPUN_COD=360100&MERCHANT=05013%7C%E5%8D%97%E6%98%8C%E5%A4%A7%E5%AD%A6%7C1740%7C0%7C%E8%AF%B7%E8%BE%93%E5%85%A5%E6%A0%A1%E5%9B%AD%E5%8D%A1%E5%8D%A1%E5%8F%B7%7C%E6%A0%A1%E5%9B%AD%E5%8D%A1%E5%8D%A1%E5%8F%B7%7C%7C0%7C%7C%7C0%7C%7C360000000%7C%7C%7C%7C%7C1011111111%7C100010%7C11%7C%7C&SJ_CONTENT=&COMM='+ \
         id + \
         '&Py_Mod=&SEQUENCE_CODE=&RE1CON=&RE2CON=&BUTTON_IMG=&BUTTON_URL=&SEQUENCE_NAME=%E8%AF%B7%E9%80%89%E6%8B%A9&REMARK1=&REMARK2=&PAGE1=&PAGE2=&TYPE1=0&DETAIL_FLAG=1011111111&TYPE2=0&BILL_NAME=%E6%A0%A1%E5%9B%AD%E5%8D%A1%E5%8D%A1%E5%8F%B7&BILL_COMM=%E8%AF%B7%E8%BE%93%E5%85%A5%E6%A0%A1%E5%9B%AD%E5%8D%A1%E5%8D%A1%E5%8F%B7&BILL_FLAG=0&TXCODE=NYS10A&BILL_ITEM=05013&OPUN_NAME=%E5%8D%97%E6%98%8C%E5%B8%82&BANK_NAME=%E6%B1%9F%E8%A5%BF%E7%9C%81&BIll_MERCHANT=1740&MERCHANT_NAME=%E5%8D%97%E6%98%8C%E5%A4%A7%E5%AD%A6&AMT_FLAG=1&CUST_FALG=&BIll_CODE=100010&BILL_TYPE=500&BRAN_NO=360000000&PAY_TYPE=11&CTPPARAM=&BEGIN_TIME=&END_TIME=&HOLIDAY_BEGIN_TIME=&HOLIDAY_END_TIME=&history_0=&history_1=&history_2=&history_3=&history_4=&history_5=&history_6=&history_7=&history_8=&history_9='
    d2 = d1.split('&')
    d3 = {}
    for x in d2:
        x = x.split('=')
        d3[x[0]] = x[1]

    res = requests.request('POST', 'http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5', headers=headers, data=d3)
    html = res.text
    if '参考消息：操作失败.可能原因:系统错误' in html:
        return {'id':id, 'name': '学号不存在', 'rest': ''}
    name_ = re.findall('<th>(.*?)</th>', html)
    rest_ = re.findall('<td>(.*?)</td>', html)


    try:
        return {'id':id, 'name': name_[-2], 'rest': rest_[-2]}
    except:
        return getRest(id, headers)




