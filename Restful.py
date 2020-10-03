from functools import wraps
import logging
from django.http import HttpResponseNotAllowed
logger = logging.getLogger('django.request')


def require(request_method_list):
    """
    Restful接口响应判断修饰器
    :param request_method_list: 可以为GET, POST, DELETE, PUT等
    :return:
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in request_method_list:
                logger.warning(
                    'Method Not Allowed (%s): %s', request.method, request.path,
                    extra={'status_code': 405, 'request': request}
                )
                return HttpResponseNotAllowed(request_method_list)
            return func(request, *args, **kwargs)
        return inner
    return decorator
