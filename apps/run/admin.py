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
admin.site.register(AthleteInfo)
admin.site.register(Position)
admin.site.register(Subscribe)


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('athlete', 'status', 'distance', 'speed', 'run_time_seconds')
