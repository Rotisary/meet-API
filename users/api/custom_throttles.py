from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework.schemas.openapi import SchemaGenerator

class BurstUserRateThrottle(UserRateThrottle):
    scope = 'burst'


class SustainedUserRateThrottle(UserRateThrottle):
    scope = 'sustained'



# class RandomRateThrottle(throttling.BaseThrottle):
#     def allow_request(self, request, view):
#         return random.randint(1, 10) != 1

class CustomSchemaGenerator(SchemaGenerator):
    pass