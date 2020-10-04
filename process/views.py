from django.shortcuts import render
from django.http import JsonResponse
import json
from RawSql import *


def index(request):
    return render(request, "PROCESS/index.html", locals())


def apply(request):
    if request.method == 'POST':
        print(request.POST.get("data"))
        for var in json.loads(request.POST.get("data")):
            print(var["value"])
    rawsql = RawSql()
    sql = "select STGMLMC from V_SJZC_GXST group by STGMLMC"  # 表获取分类
    category = rawsql.get_list(sql)
    rawsql.close()
    return render(request, "PROCESS/apply.html", locals())


def review(request):
    return render(request, "PROCESS/review.html", locals())


def tabledetail(request):
    category = request.GET.get("category", "教务管理")
    rawsql = RawSql()
    if request.method == "POST":
        sql = "select zdzwm from V_SJZC_GXST where STGMLMC='%s' and STMC='%s'  order by  zdzwm" % (category, request.POST.get("table_name"))
        res = rawsql.get_list(sql)
        data = []
        for var in res:
            if var not in ["处理日期", "WID", "备用1", "备用2", "操作类型", "数据来源"]:
                data.append(var)
        return JsonResponse({"zd": data})
    sql = "select distinct STMC, STZWM from V_SJZC_GXST where STGMLMC='%s'" % category
    data = rawsql.get_json(sql)
    if data:
        data = json.loads(data)
    else:
        data = []
    sql = "select STGMLMC from V_SJZC_GXST group by STGMLMC"  # 表获取分类
    categorys = rawsql.get_list(sql)
    rawsql.close()
    return render(request, "PROCESS/table_detail.html", locals())
