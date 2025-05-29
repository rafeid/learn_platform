# 导入 DRF 的默认异常处理器和 Response 类
from rest_framework.views import exception_handler
from rest_framework.response import Response


# 自定义异常处理函数
def custom_exception_handler(exc, context):
    # 先调用 DRF 默认的异常处理器，获取基础响应对象
    response = exception_handler(exc, context)

    # 如果默认处理器能生成响应（即异常已被 DRF 识别）
    if response is not None:
        # 重构响应数据结构，统一为 error 对象格式
        response.data = {
            'error': {
                'code': response.status_code,  # 使用 HTTP 状态码作为错误码
                'message': str(exc)  # 将异常对象转为字符串作为错误描述
            }
        }

    # 返回修改后的响应对象
    return response