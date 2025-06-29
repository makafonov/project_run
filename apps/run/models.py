from django.conf import (
    settings,
)
from django.db import (
    models,
)


class Run(models.Model):
    """Забег."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время и дата начала забега',
    )
    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='runs',
        verbose_name='Атлет',
    )
    comment = models.TextField(
        verbose_name='Комментарий',
    )

    def __str__(self) -> str:
        return f'Забег {self.id} от {self.created_at}'
