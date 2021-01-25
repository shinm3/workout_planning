from .provisional import Provisional


class ProvisionalMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        provisional_items = request.session.get('provisional')
        if provisional_items:
            provisional = Provisional.from_json(provisional_items)
        else:
            provisional = Provisional()

        request.provisional = provisional

        response = self.get_response(request)

        if request.provisional.edited:
            request.session['provisional'] = request.provisional.as_json()

        return response
