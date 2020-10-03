from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from RawSql import *
from Restful import *
import json
import requests
import re


@csrf_exempt
def dispatch_by_method(request, value=None):
    """
    一个链接解决CRUD
    :param value:
    :param request:
    :return:
    """
    import json

    ip = "http://127.0.0.1:8000"
    # 后端接口地址
    dispatches = {"POST": "/platform/add", "DELETE": "/platform/delete?pid=", "PUT": "/platform/update?pid=", "GET": "/platform/query?pid="}
    method = request.method
    request_path = dispatches[method]
    url = ip + request_path
    cookie = request.COOKIES
    if method == "POST":
        data = request.POST.get("data")
        if not data:
            data = request.body.decode("utf-8")
            data = json.loads(data)
        else:
            data = {"data": json.loads(data)}
        header = {"Content-Type": "application/json", "charset": "UTF-8"}
        return HttpResponse(requests.post(url, json=data, cookies=cookie, headers=header))
    else:
        url = url + value
        return HttpResponse(requests.get(url, cookies=cookie))


# @require('GET')
def platform_by_page(request):
    """
    根据页码获取数据接口
    :param request:
    :return:
    """
    pid = int(request.GET.get("pid", 1))
    rawsql = RawSql()
    sql = r"select * from (select t.*,rownum rn from T_XTDA  t) nn where nn.rn>%d and nn.rn=<%d" % ((pid-1)*10, pid*10)
    data = rawsql.get_json(sql)
    if data:
        data = re.sub(r'"CLRQ":.*\),', "", data)
        data = data.replace('None', '""')
        data = json.loads(data)
    else:
        data = []
    return JsonResponse({"code": "01", "msg": "query successful", "data": data}, status=200)


# @require('POST')
@csrf_exempt
def platform_insert(request):
    """
    插入数据
    :param request:
    :return:
    """
    data = request.POST.get("data", None)
    rawsql = RawSql()
    sql = rawsql.sql_bind(request, 'data', 'T_XTDA')
    if not sql:
        return JsonResponse({"code": "00", "msg": "POST参数为空"}, status=403)
    sql = re.sub('values\((\d*)', "values(SEQUENCE_BH.nextval", sql)
    print(sql)
    if rawsql.execute(sql):
        return JsonResponse({"code": "01", "msg": "insert successful"}, status=200)
    return JsonResponse({"code": "00", "msg": "insert failed, %s" % rawsql.err_msg}, status=400)


# @require('DELETE')
def platform_del_by_bh(request, pid=1):
    pass


# @require('PUT')
def platform_del_by_bh(request, pid=1):
    pass


