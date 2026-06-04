import contextvars
from ninja_jwt.authentication import JWTAuth

_current_user = contextvars.ContextVar("current_user", default=None)

def get_current_user():
    return _current_user.get()

class JWTContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth = JWTAuth()

    def __call__(self, request):
        header = request.headers.get("Authorization")
        if header and header.startswith("Bearer "):
            token = header.split(" ")[1]
            try:
                # Используем стандартный механизм аутентификации Ninja JWT
                user = self.auth.authenticate(request, token)
                if user:
                    _current_user.set(user)
            except:
                pass
        
        response = self.get_response(request)
        _current_user.set(None) # Очистка контекста
        return response
