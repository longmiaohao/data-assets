from django.shortcuts import render
from django.http import JsonResponse
from RawSql import *
import json
# Create your views here.


def index(request):
    rawsql = RawSql()
    sql = "select * from V_SJZC_HJ_XT"    # 下行数据 到中心数据
    SJHJ = rawsql.get_json(sql)
    if SJHJ:
        SJHJ = SJHJ.replace("None", '""')
        SJHJ = json.loads(SJHJ)
    else:
        SJHJ = []
    sql = "select * from V_SJZC_SY_XT"    # 上行数据 数据去处
    SJSY = rawsql.get_json(sql)
    if SJSY:
        SJSY = SJSY.replace("None", '""')
        SJSY = json.loads(SJSY)
    else:
        SJHJ = []
    response_json_L = {"name": "主数据平台", "children": [{"name": name["SXXTMC"], "more_info": name} for name in SJHJ]}
    response_json_R = {"name": "公共数据平台", "children": [{"name": name["SYXTMC"], "more_info": name} for name in SJSY]}
    return render(request, "SJGXGK/new.html", locals())


def index_old(request):
    rawsql = RawSql()
    response_json = ""
    sql = "select * from V_SJZC_HJ_XT"    # 下行数据 到中心数据
    SJHJ = rawsql.get_json(sql)
    if SJHJ:
        SJHJ = SJHJ.replace("None", '""')
        SJHJ = json.loads(SJHJ)
    else:
        SJHJ = []
    sql = "select * from V_SJZC_SY_XT"    # 上行数据 数据去处
    SJSY = rawsql.get_json(sql)
    if SJSY:
        SJSY = SJSY.replace("None", '""')
        SJSY = json.loads(SJSY)
    else:
        SJHJ = []
    step = 50
    if len(SJHJ) > len(SJSY):
        for idx, var in enumerate(SJHJ):
            var["y"] = idx*step
        total_height = len(SJHJ)*step
        step = total_height/len(SJSY)
        for idx, var in enumerate(SJSY):
            var["y"] = (idx+1)*step
    else:
        for idx, var in enumerate(SJSY):
            var["y"] = idx*step
        total_height = len(SJSY)*step
        step = total_height / len(SJHJ)
        for idx, var in enumerate(SJHJ):
            var["y"] = (idx + 1)*step
    # 曲率
    step = 0.6 / len(SJSY)  # 曲率基于-0.3到+0.3
    for idx, var in enumerate(SJSY):
        var["curveness"] = 0.3 - (idx + 1)*step

    step = 0.6 / len(SJHJ)  # 曲率基于-0.3到+0.3
    for idx, var in enumerate(SJHJ):
        var["curveness"] = 0.3 - (idx + 1) * step

    half_height = total_height/2
    rx = 2500
    lx = 0
    return render(request, "SJGXGK/index.html", locals())


def xxsj(request):
    rawsql = RawSql()
    YXTMC = request.GET.get("yxtmc", None)
    query_type = request.GET.get("type", None)
    source_name = request.GET.get("source_name", None)
    target_name = request.GET.get("target_name", None)
    HJ = request.GET.get("hj", None)
    condition = ""
    sql = ""
    if HJ:
        sql = """select * from (select ZSJXTMC XTMC, ZSJYHM YHM, ZSJSJBMC SJB, SJDXZWM ZWM from V_SJZC_HJ_SJB
union select GGXTMC XTMC, GGYHM YHM, GGSJBMC SJB, SJBZWM ZWM from V_SJZC_SY_SJB) t where XTMC='%s'""" % HJ
    if YXTMC:
        sql = """select * from (select YXTMC XTMC, YYHM YHM, SXSJB SJB, SJBZWM ZWM from V_SJZC_CS_SJB union
                select SYXTMC XTMC, SYYHM YHM, GGSJBBM SJB, SJBZWM ZWM from V_SJZC_SY_SJB) t where XTMC='%s'""" % YXTMC
    if source_name and target_name:     # 汇聚
        if query_type == '1':
            condition = "SXXTMC='%s' and ZSJXTMC='%s'" % (source_name, target_name)
            sql = "select SXXTMC, SXYHM, SXSJBMC,SXSJBMC, ZSJXTMC XXXTMC, ZSJYHM XXYHM, ZSJSJBMC XXSJBMC, SJDXZWM from V_SJZC_HJ_SJB where %s" % condition
        if query_type == '2':
            condition = "ZSJXTMC='%s' and GGXTMC='%s'" % (source_name, target_name)
            sql = "select ZSJXTMC SXXTMC, ZSJYHM SXYHM, ZSJSJBMC SXSJBMC, GGXTMC XXXTMC, GGYHM XXYHM, GGSJBBM XXSJBMC, SJBZWM SJDXZWM from V_SJZC_SJL_SJB where %s" % condition
        if query_type == '3':
            condition = "GGXTMC='%s' and SYXTMC='%s'" % (source_name, target_name)
            sql = "select GGXTMC SXXTMC, GGYHM SXYHM, GGSJBBM SXSJBMC, SYXTMC XXXTMC, SYYHM XXYHM, SJBZWM SJDXZWM from V_SJZC_SJL_SJB where %s" % condition
    data = rawsql.get_json(sql)
    if data:
        data = data.replace("None", '""')
        data = json.loads(data)
    else:
        data = []
    rawsql.close()
    return JsonResponse(data, safe=False, status=200, content_type="application/json")
