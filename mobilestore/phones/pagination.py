from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

class PhonesPagination(LimitOffsetPagination):
    default_limit = 8
    max_limit = 20

    def get_paginated_response(self, data):
        return Response(data)