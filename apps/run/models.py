from django.conf import (
    settings,
)
from django.db import (
    models,
)


class RunStatus(models.TextChoices):
    INIT = 'init'
    IN_PROGRESS = 'in_progress'
    FINISHED = 'finished'


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
    status = models.CharField(
        max_length=20,
        choices=RunStatus,
        default=RunStatus.INIT,
        verbose_name='Статус забега',
    )

    def __str__(self) -> str:
        return f'Забег {self.id} от {self.created_at}'
