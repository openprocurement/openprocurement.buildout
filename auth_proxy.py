from oslo_middleware import base
from webob.dec import wsgify
from webob.descriptors import serialize_auth
import base64


class AuthMiddleware(base.Middleware):
    @classmethod
    def factory(cls, global_conf,
                user='broker',
                password='broker'):
        cls.user = user
        cls.password = password
        return cls

    @wsgify
    def __call__(self, req):
        req.authorization = serialize_auth(('Basic', base64.b64encode('{}:{}'.format(self.user, self.password))))
        response = req.get_response(self.application)
        return response
