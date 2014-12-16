from mezzanine.core.models import Displayable, Ownable
from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from .exceptions import AlreadyExistsError
from .signals import departmentship_request_accepted, departmentship_request_rejected, departmentship_request_canceled, create_departments_group_user_created




class DepartmentGroup(Displayable, Ownable):




    def get_absolute_url(self):
        return reverse("department_group_detail", kwargs={"slug": self.slug})




class DepartmentshipRequest(models.Model):

    department_group = models.ForeignKey(DepartmentGroup)
    user = models.ForeignKey("auth.User", related_name='user')
    message = models.TextField(_('Message'), blank=True)
    created = models.DateTimeField(default=timezone.now)
    rejected = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey("auth.User", related_name='owner')
    is_admin = models.BooleanField(default=False)
    can_sign_contract = models.BooleanField(default=True)
    can_view_contract = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Departmenship Request')
        verbose_name_plural = _('Departmentship Requests')

    def __unicode__(self):
        return "Department #%d ask you #%d to join in" % (self.department_group_id, self.user_id)


    def accept(self):

        DepartmentGroupUser.objects.create(
            department_group=self.department_group,
            user = self.user,
            is_admin = self.is_admin,
            can_sign_contract=self.can_sign_contract,
            can_view_contract=self.can_view_contract
        )

        departmentship_request_accepted.send(
            sender=self,
            department_group=self.department_group,
            user = self.user,
            is_admin = self.is_admin,
            can_sign_contract=self.can_sign_contract,
            can_view_contract=self.can_view_contract
        )

        self.delete()

        return True

    def reject(self):
        self.rejected = timezone.now()
        self.save()
        departmentship_request_rejected.send(sender=self)

    def cancel(self):
        self.delete()
        departmentship_request_canceled.send(sender=self)

        return True

class DepartmentshipManager(models.Manager):



    def deparmentship_approved(self, user):
        """ Return a list of all approved contracts
        """
        qs = DepartmentGroupUser.objects.select_related('department_group', 'user').filter(user=user).all()
        deparmentship_approved = [u.from_user for u in qs]

        return deparmentship_approved


    def requests(self, user):
        """ Return A list of contract approval requests
        """
        qs = DepartmentshipRequest.objects.select_related('department_group', 'user').filter(user=user).all()
        requests = list(qs)

        return requests

    def sent_requests(self, department_group):
        """ Return a list of contract approval requests from user """

        qs = DepartmentshipRequest.objects.select_related('department_group', 'user').filter(
                department_group=department_group).all()
        requests = list(qs)

        return requests



    def rejected_requests(self, user):
        """ Return a list of rejected contract approval requests """

        qs = DepartmentshipRequest.objects.select_related('department_group', 'user').filter(
                user=user,
                rejected__isnull=False).all()
        rejected_requests = list(qs)

        return rejected_requests

    def unrejected_requests(self, user):
        """ All requests that haven't been rejected """

        qs = DepartmentshipRequest.objects.select_related('department_group', 'user').filter(
                user=user,
                rejected__isnull=True).all()
        unrejected_requests = list(qs)

        return unrejected_requests

    def unrejected_request_count(self, user):
        """ Return a count of unrejected contractship requests """

        count = DepartmentshipRequest.objects.select_related('department_group', 'user').filter(
                user=user,
            rejected__isnull=True).count()

        return count

    def create_departments_group_user(self, department_group, user):
        """ Create a contract approve request. Need to rewrite later """


        request, created = DepartmentshipRequest.objects.get_or_create(
            department_group=department_group,
            user=user,

        )

        if created is False:
            raise AlreadyExistsError("Contract has been approved")

        create_departments_group_user_created.send(sender=request)

        return request


class DepartmentGroupUser(models.Model):

    department_group = models.ForeignKey(DepartmentGroup)
    user = models.ForeignKey("auth.User")
    is_admin = models.BooleanField(default=False)
    can_sign_contract = models.BooleanField(default=True)
    can_view_contract = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    objects = DepartmentshipManager()

    class Meta:
        verbose_name = _('DepartmentGroupUser')
        verbose_name_plural = _('DepartmentGroupUsers')

    def __unicode__(self):
         return "User #%d is a staff in #%d" % (self.user_id, self.department_group_id)







