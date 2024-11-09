from user.utils import get_user_from_token

class WebSocketAuthMiddleware:
    """
    Custom ASGI middleware created to add user object in scope
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":

            # TODO: change this so that we fetch token from websocket headers itself
            query_string = scope["query_string"].decode()
            query_params = dict(pair.split('=') for pair in query_string.split('&') if '=' in pair)
            token = query_params.get("token")
            if token:
                user = get_user_from_token(token)
                scope["user"] = user
            else:
                scope["user"] = None
        await self.app(scope, receive, send)
