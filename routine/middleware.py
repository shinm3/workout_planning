from .provisional import Provisional


class ProvisionalMiddleware:
    """
    リクエストとレスポンス前後の処理になります。

    編集がなされていれば（edited=True）セッションにルーティンの設定値を入れます。
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        provisional_items = request.session.get('provisional')
        if provisional_items:  # セッションに'provisional'(ルーティンの設定値)があればそれを取り出す
            provisional = Provisional.from_json(provisional_items)
        else:  # なければ新規インスタンス化
            provisional = Provisional()
        # viewで処理される前の処理
        request.provisional = provisional
        # リクエストに対してレスポンスを返す処理（viewでの処理）
        response = self.get_response(request)
        # レスポンス後の処理
        # provisional.pyがTrueであれば（ルーティン設定で何かしらの処理を行っていれば）
        # セッション'provisional'にルーティンの設定値を格納
        if request.provisional.edited:
            request.session['provisional'] = request.provisional.as_json()

        return response
