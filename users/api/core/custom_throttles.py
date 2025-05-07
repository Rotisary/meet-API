from rest_framework.throttling import UserRateThrottle


class BurstUserRateThrottle(UserRateThrottle):
    scope = 'burst'


class SustainedUserRateThrottle(UserRateThrottle):
    scope = 'sustained'



# class RandomRateThrottle(throttling.BaseThrottle):
#     def allow_request(self, request, view):
#         return random.randint(1, 10) != 1
