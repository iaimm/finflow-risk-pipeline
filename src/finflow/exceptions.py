class FinFlowError(Exception):
    """项目业务异常的基类。"""


class ValidationError(FinFlowError):
    """输入或业务数据不符合规则。"""


class NotFoundError(FinFlowError):
    """请求的业务对象不存在。"""


class ConflictError(FinFlowError):
    """当前操作与已有数据冲突。"""


class AuthenticationError(FinFlowError):
    """身份认证失败。"""


class AuthorizationError(FinFlowError):
    """身份有效，但没有执行操作的权限。"""