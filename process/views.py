from django.shortcuts import render
from django.http import JsonResponse
import json
from RawSql import *


def index(request):
    return render(request, "PROCESS/index.html", locals())


def apply(request):
    rawsql = RawSql()
    sql = "select STGMLMC from V_SJZC_GXST group by STGMLMC"  # 表获取分类
    print(sql)
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
        data = rawsql.get_list(sql)
        rawsql.close()
        data.remove("处理日期")
        data.remove("WID")
        data.remove("备用1")
        data.remove("备用2")
        data.remove("操作类型")
        data.remove("数据来源")
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
