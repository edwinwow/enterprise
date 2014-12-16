from rest_framework import serializers
from .models import DepartmentGroup, DepartmentGroupUser, DepartmentshipRequest
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from makenewcontract.models import Contract
from django.db.models import Q


class DepartmentGroupModelSerializer(serializers.ModelSerializer):


    class Meta:
        model = DepartmentGroup
        fields = ('id', 'title', 'description', 'created')

class DepartmentshipRequestModelSerializer(serializers.ModelSerializer):


    class Meta:
        model = DepartmentshipRequest
        fields = ('id', 'department_group', 'user', 'message', 'rejected', 'is_admin', 'can_sign_contract', 'can_view_contract')



class DepartmentshipRequestModifyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentshipRequest
        fields = ('id', 'department_group', 'user', 'message', 'rejected', 'is_admin', 'can_sign_contract', 'can_view_contract')

class ContactCountField(serializers.Field):

    pub_date = datetime.now()

    def to_native(self, value, request):
        user = request.user

        score_sum = Contract.objects.filter(Q(company_a = user) or Q (company_b = user) ).extra(select={'month': 'extract( month from pub_date )'}).values('month').annotate(dcount=Count('created_date'))
        if score_sum is not None:
            return int(score_sum / value.count())
        else:
            return None


class DepartmentGroupUserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentGroupUser
        fields = ('id', 'department_group', 'user', 'is_admin', 'can_sign_contract', 'can_view_contract', 'created')
        depth = 1

class DepartmentGroupUserModelCreateSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = DepartmentGroupUser
        fields = ('id', 'department_group', 'user', 'is_admin', 'can_sign_contract', 'can_view_contract', 'created')



class DepartmentGroupUserModifyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentGroupUser
        fields = ('id', 'department_group', 'user', 'is_admin', 'can_sign_contract', 'can_view_contract', 'created')


