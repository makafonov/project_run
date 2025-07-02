from django.contrib import (
    admin,
)

from apps.run.models import (
    AthleteInfo,
    Challenge,
    Run,
)


admin.site.register(Challenge)
admin.site.register(Run)
admin.site.register(AthleteInfo)
