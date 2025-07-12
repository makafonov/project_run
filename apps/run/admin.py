from django.contrib import (
    admin,
)

from apps.run.models import (
    AthleteInfo,
    Challenge,
    CollectibleItem,
    Position,
    Run,
    Subscribe,
)


admin.site.register(Challenge)
admin.site.register(CollectibleItem)
admin.site.register(Run)
admin.site.register(AthleteInfo)
admin.site.register(Position)
admin.site.register(Subscribe)
