from django.shortcuts import render, redirect
from django.http import JsonResponse
from RawSql import *
import math
import json
import re
from Utils.AES import Aes
from django.views.decorators.csrf import csrf_exempt

set_page_num = 10  # 分页单页数量


def get_page_info(table_name=None, num_per_page=20, condition=''):
    if not table_name:
        raise Exception("未知表名")
    rawsql = RawSql()
    sql = "select count(*) pagenum from %s where CZLX!='D' %s" % (table_name, condition)
    try:
        data = rawsql.get_list(sql)
    except Exception as e:
        raise e
    return {"page_num": math.ceil(data[0]/num_per_page), "num": data[0]}


def xtda_index(request):
    """
    查询逻辑：系统类型，管理单位，职工号，系统名称模糊搜索
    :param request:
    :return:
    """
    page = int(request.POST.get("page", 1))    # 默认第一页 利用form表单填写
    lx = request.GET.get("lx", None)    # 类型过滤参数
    if not lx:
        lx = request.POST.get("lx", None)
    GLDWDM = request.POST.get("dw_query", "")
    if not GLDWDM:
        GLDWDM = request.GET.get("dw_query", "")
    keyword = request.POST.get("keyword", "")
    if not keyword:
        keyword = request.GET.get("keyword", "")
    ZGH = ""
    MC = ""
    if keyword:
        ZGH = re.match(r"(\d+)", keyword)   # 判断是否是工号参数
        if ZGH:
            ZGH = keyword
        else:
            MC = keyword    # 不是职工号就是系统名称
    condition = ""
    if lx:
        condition += " and lx='%s'" % lx
    if GLDWDM:
        condition += " and GLDWDM='%s'" % GLDWDM
    if ZGH:
        condition += "and GLYZGH like '%%%s%%'" % ZGH
    if MC:
        condition += "and JC like '%%%s%%' or ZWM like '%%%s%%'" % (MC, MC)
    if condition:  # 带类型过滤搜索
        page_info = get_page_info('T_XTDA', set_page_num, condition)
        sql = "select * from (select t.*,rownum rn from V_XTDA  t where CZLX!='D' %s) nn where nn.rn>%d and nn.rn<=%d order by JDRQ desc" % (condition, (page-1)*set_page_num, page*set_page_num)
    else:   # 不带类型过滤搜索
        page_info = get_page_info('T_XTDA', set_page_num)
        sql = "select * from (select t.*,rownum rn from V_XTDA  t where CZLX!='D') nn where nn.rn>%d and nn.rn<=%d order by JDRQ desc" % (
        (page - 1) * set_page_num, page * set_page_num)
    rawsql = RawSql()
    data = []
    try:
        data = rawsql.get_json(sql)
    except:
        data = None
        err_msg = rawsql.err_msg
    if data:
        data = re.sub(r'"CLRQ":.{0,45}\),', "", data)
        data = data.replace('None', '""')
        data = json.loads(data)
    else:
        data = []
    # 系统类型
    sql = "select DM, MC from T_XTDA_XTLX"
    XTLX = rawsql.get_json(sql)
    XTLX = json.loads(XTLX)
    show_title = ""     # 系统类型展示
    if lx:
        for var in XTLX:
            if int(var["DM"]) == int(lx):
                show_title = var["MC"]
    else:
        show_title = "全部"
    sql = "select distinct t2.DWDM, t2.DWMC MC from T_XTDA t1, T_XX_DW t2 where t1.GLDWDM=t2.DWDM and t1.CZLX!='D'"
    GLDWDMs = rawsql.get_json(sql)
    if GLDWDMs:
        GLDWDMs = json.loads(GLDWDMs)
    # 用户类型 新增系统用户
    sql = "select MC, DM from T_XTDA_SJTBYHLX where CZLX!='D'"
    YHLXS = rawsql.get_json(sql)
    if YHLXS:
        YHLXS = json.loads(YHLXS)
    else:
        YHLXS = []
    return render(request, "XTDA/index.html", locals(), status=200)

# def xtda_index_table(request):
#     # 系统类型
#     lx = request.GET.get("lx", None)    # 类型过滤参数
#     if not lx:
#         lx = request.POST.get("lx", None)
#     rawsql = RawSql()
#     sql = "select DM, MC from T_XTDA_XTLX"
#     XTLX = rawsql.get_json(sql)
#     XTLX = json.loads(XTLX)
#     show_title = ""     # 系统类型展示
#     if lx:
#         for var in XTLX:
#             if int(var["DM"]) == int(lx):
#                 show_title = var["MC"]
#     else:
#         show_title = "全部"
#     sql = "select distinct t2.DWDM, t2.DWMC MC from T_XTDA t1, T_XX_DW t2 where t1.GLDWDM=t2.DWDM and t1.CZLX!='D'"
#     GLDWDMs = rawsql.get_json(sql)
#     if GLDWDMs:
#         GLDWDMs = json.loads(GLDWDMs)
#     # 用户类型 新增系统用户
#     sql = "select MC, DM from T_XTDA_SJTBYHLX where CZLX!='D'"
#     YHLXS = rawsql.get_json(sql)
#     if YHLXS:
#         YHLXS = json.loads(YHLXS)
#     else:
#         YHLXS = []
#     return render(request, "XTDA/index.html", locals())


def xtda_add(request):
    rawsql = RawSql()
    # 系统类型
    sql = "select DM, MC from T_XTDA_XTLX"
    XTLX = rawsql.get_json(sql)
    XTLX = json.loads(XTLX)
    # 服务器类型
    sql = "select DM, MC from T_XTDA_FWQLX"
    FWQLX = rawsql.get_json(sql)
    FWQLX = json.loads(FWQLX)
    # 数据库类型
    sql = "select DM, MC from T_XTDA_SJKLX"
    SJKLX = rawsql.get_json(sql)
    SJKLX = json.loads(SJKLX)
    # 管理单位
    sql = "select  t.DWMC MC, t.DWDM, t.rowid from t_xx_dw t where t.dwcc='1' and t.sfsy='1' order by t.dwlbdm,t.dwdm"
    GLDWDMs = rawsql.get_json(sql)
    if GLDWDMs:
        GLDWDMs = json.loads(GLDWDMs)
    if request.method == "POST":
        post = request.POST
        LX = post.get("LX", "")
        ZWM = post.get("ZWM", "")
        JC = post.get("JC", "")
        GLYXM = post.get("GLYXM", "")
        GLYZGH = post.get("GLYZGH", "")
        GLDWDM = post.get("GLDWDM", "")
        YYFWQIP = post.get("YYFWQIP", "")
        YYFWQLXDM = post.get("YYFWQLXDM", "")
        SJKFWQIP = post.get("SJKFWQIP")
        SJKFWQLXDM = post.get("SJKFWQLXDM", "")
        SJKLXDM = post.get("SJKLXDM", "")
        SJKBB = post.get("SJKBB", "")
        SJLY = post.get("SJLY", "")
        JDRQ = post.get("JDRQ", "")
        SCCJ = post.get("SCCJ", "")
        BH = request.POST.get("BH", None)
        if not GLYXM or not GLDWDM:
            err_msg = "星号字段不可为空"
            return render(request, "XTDA/add.html", locals())
        if BH:
            sql = "update T_XTDA set LX='%s', ZWM='%s', JC='%s', GLYXM='%s', GLYZGH='%s', GLDWDM='%s', YYFWQIP='%s', YYFWQLXDM='%s', SJKFWQIP='%s', SJKFWQLXDM='%s', SJKBB='%s', SJLY='%s', SCCJ='%s', JDRQ='%s', CZLX='U', CLRQ=sysdate, SJKLXDM='%s' where BH=%s" % (LX, ZWM, JC, GLYXM, GLYZGH, GLDWDM, YYFWQIP, YYFWQLXDM, SJKFWQIP, SJKFWQLXDM, SJKBB, SJLY, SCCJ, JDRQ, SJKLXDM, BH)
        else:
            values = "%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', 'I', '%s'" % ("SQ_T_XTDA.nextval", LX, ZWM, JC, GLYXM, GLYZGH, GLDWDM, YYFWQIP, YYFWQLXDM, SJKFWQIP, SJKFWQLXDM, SJKBB, SJLY, SCCJ, JDRQ, SJKLXDM)
            sql = "insert into T_XTDA(BH,LX, ZWM, JC, GLYXM, GLYZGH, GLDWDM, YYFWQIP, YYFWQLXDM, SJKFWQIP, SJKFWQLXDM, SJKBB, SJLY, SCCJ, JDRQ, CZLX, SJKLXDM) values(%s)" % values
        if rawsql.execute(sql):
            return redirect("/xtda")
        else:
            err_msg = rawsql.err_msg
            return render(request, "XTDA/add.html", locals(), status=200)
    title = "新增系统档案"
    return render(request, "XTDA/add.html", locals(), status=200)


def xtda_delete(request):
    BH = request.POST.get("BH", None)
    BH = BH.split(",") # 将要删除的编号
    rawsql = RawSql()
    sql = "select distinct t.SSXTBH from V_XTDA_SJTBYH t where CZLX!='D'"
    BHS = rawsql.get_list(sql)  # 不能删除的编号
    intersection = [x for x in BH if int(x) in set(BHS)] # 不能删的编号
    diff = [int(x) for x in set(BH) if x not in intersection]    # 可以删除的编号
    if not diff:
        return JsonResponse({"code": "01", "msg": "successful", "intersection": intersection, "diff": diff}, status=200)
    sql = "update T_XTDA set CZLX='D', CLRQ=sysdate where BH in (%s)" % str(diff)[1:-1]
    if rawsql.execute(sql):
        rawsql.close()
        return JsonResponse({"code": "01", "msg": "successful", "intersection": intersection, "diff": diff}, status=200)
    else:
        rawsql.close()
        return JsonResponse({"code": "00", "msg": '"' + rawsql.err_msg + '"'}, status=200)


def xtda_edit(request):
    title = "编辑系统档案"
    BH = request.GET.get("bh", None)
    if not BH:
        return JsonResponse({"code": "01", "msg": "illegal BH"}, status=403)
    sql = "select * from V_XTDA where BH=%s" % BH
    rawsql = RawSql()
    data = rawsql.get_json(sql)
    if data:
        data = re.sub(r'"CLRQ":.{0,45}\),', "", data)
        data = data.replace('None', '""')
        data = json.loads(data)[0]
        # 系统类型
        sql = "select DM, MC from T_XTDA_XTLX"
        XTLX = rawsql.get_json(sql)
        XTLX = json.loads(XTLX)
        # 服务器类型
        sql = "select DM, MC from T_XTDA_FWQLX"
        FWQLX = rawsql.get_json(sql)
        FWQLX = json.loads(FWQLX)
        # 数据库类型
        sql = "select DM, MC from T_XTDA_SJKLX"
        SJKLX = rawsql.get_json(sql)
        SJKLX = json.loads(SJKLX)
        # 管理单位
        sql = "select t.DWMC MC, t.DWDM, t.rowid from t_xx_dw t where t.dwcc='1' and t.sfsy='1' order by t.dwlbdm,t.dwdm"
        GLDWDMs = rawsql.get_json(sql)
        if GLDWDMs:
            GLDWDMs = json.loads(GLDWDMs)
        return render(request, "XTDA/add.html", locals())
    else:
        return JsonResponse({"code": "01", "msg": "illegal BH"}, status=403)


def get_dw_xm_by_zgh(request):
    import requests
    ZGH = request.POST.get("ZGH")
    if ZGH:
        url = "http://apis.scuec.edu.cn:80/gxsj/jzg"
        appId = "f3b156cb38b514bd"
        accessToken = "ad06edd88c46eb10e0da997bc749dfae"
        header = {"appId": appId, "accessToken": accessToken}
        post_json = {"ZGH": ZGH}
        data = requests.post(url, headers=header, json=post_json)
        data = json.loads(data.text)
        if data["RTN_CODE"] != "01":    # 查询失败不执行
            dwmc = data["DATA"][0]["DWMC"]
            sql = "select DWDM from T_XX_DW where DWMC='%s'" % dwmc
            rawsql = RawSql()
            dwdm = rawsql.get_list(sql)
            data["DATA"][0]["DWDM"] = dwdm[0]
            return JsonResponse(data, status=200)
    return JsonResponse({"code": "00", "msg": "查询失败"}, status=200)


def yhda_index(request):
    """
    数据库用户档案
    :param request:
    :return:
    """
    lx = request.GET.get("lx", None)    # 类型过滤参数
    page = int(request.POST.get("page", 1))    # 默认第一页 利用form表单填写
    if not lx:
        lx = request.POST.get("lx", None)
    GLDWDM = request.POST.get("dw_query", "")
    if not GLDWDM:
        GLDWDM = request.GET.get("dw_query", "")
    keyword = request.POST.get("keyword", "")
    if not keyword:
        keyword = request.GET.get("keyword", "")
    condition = ""
    SSXTBH = request.GET.get("ssxtbh", None)
    # sql条件
    if lx:
        condition += " and YHLX='%s'" % lx
    if keyword:
        condition += "and YHM like '%%%s%%'" % keyword
    if GLDWDM:
        condition += "and GLDWDM=%s" % GLDWDM
    if SSXTBH:
        condition += "and SSXTBH=%s" % SSXTBH

    if condition:
        sql = "select * from (select t.*,rownum rn from V_XTDA_SJTBYH  t where CZLX!='D' %s) nn where nn.rn>%d and nn.rn<=%d"  % (
        condition, (page - 1) * set_page_num, page * set_page_num)
    else:
        sql = "select * from (select t.*,rownum rn from V_XTDA_SJTBYH  t) nn where nn.rn>%d and nn.rn<=%d and CZLX!='D'" % ((page-1)*set_page_num, page*set_page_num)
    rawsql = RawSql()
    data = rawsql.get_json(sql)
    if data:
        data = re.sub(r'"CLRQ":.{0,45}\),', "", data)
        data = data.replace('None', '""')
        data = json.loads(data)
    else:
        data = []
    page_info = get_page_info("V_XTDA_SJTBYH", set_page_num, condition)
    sql = "select DM, MC from T_XTDA_SJTBYHLX"
    YHLXS = rawsql.get_json(sql)
    if YHLXS:
        YHLXS = json.loads(YHLXS)
    # 用户类型
    sql = "select DM, MC from T_XTDA_SJTBYHLX"
    YHLX = rawsql.get_json(sql)
    YHLX = json.loads(YHLX)
    show_title = ""  # 系统类型展示
    if lx:
        for var in YHLX:
            if int(var["DM"]) == int(lx):
                show_title = var["MC"]
    else:
        show_title = "全部"
    # sql = "select distinct GLDWDM DWDM, GLDWMC DWMC from V_XTDA_SJTBYH"
    sql = "select distinct t2.DWDM DWDM, t2.DWMC DWMC from T_XTDA t1, T_XX_DW t2 where t1.GLDWDM=t2.DWDM and t1.CZLX!='D'"
    GLDWDMs = rawsql.get_json(sql)
    if GLDWDMs:
        GLDWDMs = json.loads(GLDWDMs)
    else:
        GLDWDMs = []
    rawsql.close()
    return render(request, "YHDA/index.html", locals())


def yhda_add(request):
    title = "用户档案新增"
    rawsql = RawSql()
    sql = "select MC, DM from T_XTDA_SJTBYHLX where CZLX!='D'"
    YHLXS = rawsql.get_json(sql)
    if YHLXS:
        YHLXS = json.loads(YHLXS)
    else:
        YHLXS = []
    # 所属系统
    sql = "select ZWM, BH from V_XTDA where CZLX!='D'"
    SSXT = rawsql.get_json(sql)
    if SSXT:
        SSXT = json.loads(SSXT)
    else:
        SSXT = []
    # 修改
    YHBH = request.POST.get("YHBH", None)
    MM = request.POST.get("MM", '')
    if YHBH:
        YHLX = request.POST.get("YHLX", None)
        YHM = request.POST.get("YHM", None)
        SSXTBH = request.POST.get("SSXTBH", None)
        sql = ""
        if MM:  # 有密码改密码
            aes = Aes()   # 32位的密钥的AES
            cypher = aes.encrypt(MM)    # 加密密码的字符串
            secret_key = aes.secret_key
            SSXTBH = int(request.POST.get("SSXTBH", None))
            sql = "update T_XTDA_SJTBYH set YHLX='%s', YHM='%s', MM='%s', SSXTBH=%s, CLRQ=sysdate, CZLX='U' where YHBH=%s" % (
        YHLX, YHM, cypher, SSXTBH, YHBH)
        else:
            sql = "update T_XTDA_SJTBYH set YHLX='%s', YHM='%s', SSXTBH=%s, CLRQ=sysdate, CZLX='U' where YHBH=%s" % (
                YHLX, YHM, SSXTBH, YHBH)
        if rawsql.execute(sql):
            if MM:  # 有密码改密钥
                sql = "insert into T_YHDA_SECRET_KEY(YHBH, SECRET_KEY) values (%s, '%s')" % (YHBH, secret_key) # 先插入
                if not rawsql.execute(sql): # 更新密钥表
                    sql = "update T_YHDA_SECRET_KEY set SECRET_KEY='%s' where YHBH=%s" % (secret_key, YHBH)    # 后更新
                    rawsql.execute(sql)
            rawsql.close()
            return redirect("yhda_index")
        else:
            err_msg = rawsql.err_msg
            return render(request, "YHDA/add.html", locals())
    # 新增
    if request.method == "POST":
        YHLX = request.POST.get("YHLX", "")
        YHM = request.POST.get("YHM", "")
        MM = request.POST.get("MM", "")
        SSXTBH = int(request.POST.get("SSXTBH", ""))
        aes = Aes(32)   # 32位的密钥的AES
        cypher = aes.encrypt(MM)    # 加密密码的字符串
        secret_key = aes.secret_key
        sql = "insert into T_XTDA_SJTBYH(YHBH, YHLX, YHM, MM, SSXTBH, CZLX, CLRQ) values (%s, '%s', '%s', '%s', %s, '%s', %s)" % ('SQ_T_XTDA_SJTBYH.nextval', YHLX, YHM, cypher, SSXTBH, "I", "sysdate")
        if rawsql.execute(sql):
            sql = "select SQ_T_XTDA_SJTBYH.currval from dual"  # 获取用户编号
            try:
                YHBH = rawsql.get_list(sql)[0]
            except Exception:
                err_msg = rawsql.err_msg
                rawsql.close()
                return render(request, "YHDA/add.html", locals())
            sql = "insert into T_YHDA_SECRET_KEY(YHBH, SECRET_KEY) values(%s, '%s')" % (YHBH, secret_key)
            if not rawsql.execute(sql): # 密钥插入失败 则回滚
                sql = "delete from T_XTDA_SJTBYH where YHBH=%s" % YHBH
                rawsql.execute(sql)
                err_msg = rawsql.err_msg
                rawsql.close()
                if request.POST.get("modal", None): # 模态框提交
                    return JsonResponse({"code": "00", "msg": "faild", "err_msg": rawsql.err_msg}, status=200)
                return render(request, "YHDA/add.html", locals())
            rawsql.close()
            if request.POST.get("modal", None): # 模态框提交
                return JsonResponse({"code": "01", "msg": "successful"}, status=200)
            return redirect("/yhda_index")
        else:
            rawsql.close()
            err_msg = rawsql.err_msg
            return render(request, "YHDA/add.html", locals())
    rawsql.close()
    return render(request, "YHDA/add.html", locals())


def yhda_edit(request):
    title = "编辑用户档案"
    YHBH = request.GET.get("yhbh", None)
    if not YHBH:
        return JsonResponse({"code": "01", "msg": "illegal YHBH"}, status=403)
    sql = "select * from V_XTDA_SJTBYH where YHBH=%s" % YHBH
    rawsql = RawSql()
    data = rawsql.get_json(sql)
    if data:
        data = re.sub(r'"CLRQ":.{0,45}\),', "", data)
        data = data.replace('None', '""')
        data = json.loads(data)[0]
        data["MM"] = ""
        sql = "select MC, DM from T_XTDA_SJTBYHLX where CZLX!='D'"
        YHLXS = rawsql.get_json(sql)
        if YHLXS:
            YHLXS = json.loads(YHLXS)
        else:
            YHLXS = []
        # 所属系统
        sql = "select ZWM, BH from V_XTDA where CZLX!='D'"
        SSXT = rawsql.get_json(sql)
        if SSXT:
            SSXT = json.loads(SSXT)
        else:
            SSXT = []
        return render(request, "YHDA/add.html", locals())
    else:
        return JsonResponse({"code": "01", "msg": "illegal YHBH"}, status=403)


def yhda_delete(request):
    YHBH = request.POST.get("YHBH", None)
    sql = "update T_XTDA_SJTBYH set CZLX='D', CLRQ=sysdate where YHBH in (%s)" % YHBH
    rawsql = RawSql()
    if rawsql.execute(sql):
        sql = "delete from T_YHDA_SECRET_KEY where YHBH in (%s)" % YHBH
        rawsql.execute(sql)
        rawsql.close()
        return JsonResponse({"code": "01", "msg": "successful", "err_msg": '"' + rawsql.err_msg + '"'}, status=200)
    else:
        rawsql.close()
        return JsonResponse({"code": "00", "msg": "failed", "erro_msg": '"' + rawsql.err_msg + '"'}, status=200)


def yhda_decrypt(request):
    YHBH = request.POST.get("YHBH", None)
    if YHBH:
        sql = "select t1.MM, t2.SECRET_KEY from T_XTDA_SJTBYH t1, T_YHDA_SECRET_KEY t2 where t1.YHBH=t2.YHBH and t1.YHBH=%s" % YHBH
        rawsql = RawSql()
        data = rawsql.get_json(sql)
        plaintext = ""
        if data:
            data = json.loads(data)
            secret_key = data[0]["SECRET_KEY"]
            mm = data[0]["MM"]
            aes = Aes()
            plaintext = aes.decrypt(mm, secret_key)
        return JsonResponse({"code": "01", "msg": "successful", "plaintext": plaintext}, status=200)
    else:
        return JsonResponse({"code": "00", "msg": "failed"}, status=403)


def yhda_ssxtyh(request):
    XTBH = request.POST.get("SSXTBH", None)
    if XTBH:
        rawsql = RawSql()
        sql = "select YHBH, YHM, YHLXMC, MM, SSXTMC, GLDWMC, SJKFWQIP, SJKFWQLXMC, SJKBB from V_XTDA_SJTBYH where CZLX!='D' and SSXTBH=%s" % XTBH
        data = rawsql.get_json(sql)
        data = data.replace("None",'""')
        if data:
            data = json.loads(data)
        else:
            data = []
        return JsonResponse({"code": "01", "msg": "successful", "data": data}, status=200)
    return JsonResponse({"code": "00", "msg": "非法访问"}, status=403)


def xtda_data(request):
    sql = "select * from V_XTDA"
    rawsql = RawSql()
    data = rawsql.get_json(sql)
    if data:
        data = re.sub(r'"CLRQ":.{0,45}\),', "", data)
        data = data.replace('None', '""')
        data = json.loads(data)
    else:
        data = []
    rawsql.close()
    return JsonResponse(data, safe=False, status=200)

