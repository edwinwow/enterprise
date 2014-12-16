from rest_framework import generics
from .serializers import DepartmentGroupModelSerializer, DepartmentshipRequestModelSerializer, DepartmentshipRequestModifyModelSerializer, \
    DepartmentGroupUserModelSerializer, DepartmentGroupUserModifyModelSerializer, DepartmentGroupUserModelCreateSerializer
from .models import DepartmentGroup,  DepartmentGroupUser, DepartmentshipRequest
from rest_framework import permissions
from rest_framework.decorators import api_view
from mezzanine.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action, link
from .signals import departmentship_request_accepted, departmentship_request_rejected, departmentship_request_canceled, create_departments_group_user_created


from rest_framework.response import Response
from django.utils import timezone
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from django.utils import timezone




class DepartmentshipRequestViewSet(CacheResponseMixin, viewsets.ModelViewSet):

    queryset = DepartmentshipRequest.objects.all()
    serializer_class = DepartmentshipRequestModelSerializer
    paginate_by = 15
    paginate_by_param = 'page_size'
    max_paginate_by = 100




    @action()
    def accept(self, request, pk=None):
        """ Accept this contract approval request
        """
        obj = DepartmentshipRequest.objects.get(pk=pk)



        DepartmentGroupUser.objects.create(
            department_group=obj.department_group,
            user = obj.user
        )


        departmentship_request_accepted.send(
            sender=obj,
            department_group=obj.department_group,
            user = obj.user

        )

        obj.delete()

        # Delete any reverse requests
        DepartmentshipRequest.objects.filter(
            department_group=obj.department_group,
            user = obj.user
        ).delete()

        return Response({'You have joined this department'})

    @action()
    def reject(self, request, pk=None):

        """ reject this contract approve request """

        obj =DepartmentshipRequest.objects.get(pk=pk)
        obj.rejected = timezone.now()
        obj.save()
        departmentship_request_rejected.send(sender=obj)
        return Response({'this request is rejected'})

    @action()
    def cancel(self, request, pk=None):
        """ cancel this friendship request """
        obj = DepartmentshipRequest.objects.get(pk=pk)
        obj.delete()
        departmentship_request_canceled.send(sender=obj)
        return Response({'this request is cancelled'})

    def pre_save(self, obj):
        obj.owner = self.request.user






class DepartmentshipRequestCreateAPI(generics.ListCreateAPIView):
    queryset = DepartmentshipRequest.objects.all()
    model = DepartmentshipRequest
    serializer_class = DepartmentshipRequestModifyModelSerializer

    paginate_by = 15
    paginate_by_param = 'page_size'
    max_paginate_by = 100


    def pre_save(self, obj):
        obj.owner = self.request.user






class DeaprtmentshipRequestDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    model = DepartmentshipRequest
    serializer_class = DepartmentshipRequestModelSerializer


class DepartmentGroupUserCreateAPI(generics.CreateAPIView):
    model = DepartmentGroupUser
    serializer_class = DepartmentGroupUserModelCreateSerializer



class DepartmentGroupUserListAPI( generics.ListAPIView):
    model = DepartmentGroupUser
    serializer_class = DepartmentGroupUserModelSerializer

    paginate_by = 15
    paginate_by_param = 'page_size'
    max_paginate_by = 100



class DepartmentGroupUserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    model = DepartmentGroupUser
    serializer_class = DepartmentGroupUserModelSerializer



class DepartmentGroupCreateAPI(generics.CreateAPIView):
    model = DepartmentGroup
    serializer_class = DepartmentGroupModelSerializer

    def pre_save(self, obj):
        obj.user = self.request.user
        obj.created = timezone.now()



class DepartmentGroupListAPI(generics.ListAPIView):
    model = DepartmentGroup
    serializer_class = DepartmentGroupModelSerializer

    paginate_by = 15
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class DepartmentGroupDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    model = DepartmentGroup
    serializer_class = DepartmentGroupModelSerializer


class UserDepartmentGroupAPI(generics.ListAPIView):


    model = DepartmentGroupUser
    serializer_class = DepartmentGroupUserModelSerializer

    def get_queryset(self):

        user = self.request.user
        return DepartmentGroupUser.objects.filter(user=user)



