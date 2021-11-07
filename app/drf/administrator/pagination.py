from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
	page_size = 20

	def get_paginated_response(self, data):
		# print(self.page.paginator.page_range)
		return Response({
			'links': {
				'next': self.get_next_link(),
				'previous': self.get_previous_link()
			},
			'count': self.page.paginator.count,
			'page_range': len(self.page.paginator.page_range),
			'results': data
		})
