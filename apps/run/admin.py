from django.contrib import (
    admin,
)

from apps.run.models import (
    AthleteInfo,
    Challenge,
    CollectibleItem,
    Run,
)


admin.site.register(Challenge)
admin.site.register(CollectibleItem)
admin.site.register(Run)
admin.site.register(AthleteInfo)
