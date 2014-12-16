from django.dispatch import Signal


create_departments_group_user_created = Signal()
departmentship_request_rejected = Signal()
departmentship_request_canceled = Signal()
departmentship_request_accepted = Signal(providing_args=['department_group', 'user'])

