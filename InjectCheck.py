from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
import re
import time
from django.conf import settings


class InjectCheck(MiddlewareMixin):
    """sql注入检测： 过滤恶意查询， 过滤恶意操作
     02代码 入参异常, 不能传入 '='
     03代码 检测到sql注入
    之所以多一个关于'='符号的检测，因为这个符号会对程序运行产生影响，让接收到的数据无法正常解析"""
    __msg = ''

    def process_request(self, request):
        if not settings.DEBUG:
            if request.method == 'GET':
                return HttpResponse("非法访问")
        try:
            check_data = request.body.decode('utf8')
        except:
            self.__msg = '{"RTN_CODE": "02", "DATA": [], "RTN_MSG": "未知异常参数数据解析失败!"})'
            with open('sql_inject_log.txt', 'a') as f:
                f.write("ip: " + request.META["REMOTE_ADDR"] + "    time:" + time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                           time.localtime())
                        + "     params:" + check_data + '\n')
                f.close()
            return HttpResponse(status=400, content=self.__msg)
        check_result = re.search(r'[\',\"]?\s*((or)|(union)|(and))+\s*[\',\"]?\w+[\',\"]?\s*=\s*[\',\"]?\w+\s*(--)?', check_data, re.I)
        if check_result:
            with open('sql_inject_log.txt', 'a') as f:
                f.write("ip: " + request.META["REMOTE_ADDR"] + "    time:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        + "     params:" + check_data + "    inject:" + check_result.group(0) + '\n')
                f.close()
            self.__msg = '{"RTN_CODE": "03", "DATA": [], "RTN_MSG": "发现sql注入!"})'
            return HttpResponse(status=400, content=self.__msg)
        check_result = re.search(r'[\',\"]?\s*[\',\"]?((delete)|(union)|(update)|(drop)|(truncate)|(create)|(select))+\s*\*?\s+[\',\"]?', check_data, re.I)
        if check_result:
            with open('sql_inject_log.txt', 'a') as f:
                f.write("ip: " + request.META["REMOTE_ADDR"] + "    time:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        + "     params:" + check_data + "    inject:" + check_result.group(0) + '\n')
                f.close()
            self.__msg = '{"RTN_CODE": "03", "DATA": [], "RTN_MSG": "发现sql注入!"})'
            return HttpResponse(status=400, content=self.__msg)
