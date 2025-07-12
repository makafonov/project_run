from django.conf import (
    settings,
)
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
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
    distance = models.FloatField(
        verbose_name='Дистанция забега',
        null=True,
    )
    run_time_seconds = models.IntegerField(
        verbose_name='Общее время забега в секундах',
        null=True,
        blank=True,
    )
    speed = models.FloatField(
        verbose_name='Средняя скорость всех позиций',
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f'Забег {self.id} ({self.athlete}) от {self.created_at}'


class AthleteInfo(models.Model):
    """Информация об атлете."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='athlete_info',
        verbose_name='Атлет',
    )
    goals = models.TextField(
        verbose_name='Цели атлета',
    )
    weight = models.IntegerField(
        verbose_name='Вес атлета',
        null=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(899),
        ),
    )

    def __str__(self) -> str:
        return f'Информация атлета {self.user_id}'


class Challenge(models.Model):
    """Челлендж атлета."""

    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenges',
        verbose_name='Атлет',
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name='Название челленджа',
    )

    def __str__(self) -> str:
        return f'Челлендж {self.full_name} атлета {self.athlete_id}'


class Position(models.Model):
    """Координата забега."""

    run = models.ForeignKey(
        Run,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='Забег',
    )
    latitude = models.FloatField(
        verbose_name='Широта',
        validators=(
            MinValueValidator(-90.0),
            MaxValueValidator(90.0),
        ),
    )
    longitude = models.FloatField(
        verbose_name='Долгота',
        validators=(
            MinValueValidator(-180.0),
            MaxValueValidator(180.0),
        ),
    )
    date_time = models.DateTimeField(null=True)
    speed = models.FloatField(
        verbose_name='Скорость в м/с относительно предыдущей позиции',
        null=True,
        blank=True,
    )
    distance = models.FloatField(
        verbose_name='Расстояние с учетом предыдущих позиций',
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f'Координата забега {self.run_id} - ({self.latitude}, {self.longitude})'


class CollectibleItem(models.Model):
    """Коллекционный предмет."""

    name = models.CharField(
        verbose_name='Название предмета',
        max_length=100,
    )
    uid = models.CharField(
        verbose_name='Идентификатор предмета',
        max_length=100,
    )
    latitude = models.FloatField(
        verbose_name='Широта',
        validators=(
            MinValueValidator(-90.0),
            MaxValueValidator(90.0),
        ),
    )
    longitude = models.FloatField(
        verbose_name='Долгота',
        validators=(
            MinValueValidator(-180.0),
            MaxValueValidator(180.0),
        ),
    )
    value = models.IntegerField()
    picture = models.URLField(verbose_name='Ссылка на картинку')
    athlete = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='items',
        verbose_name='Атлет',
    )

    def __str__(self) -> str:
        return f'Коллекционный предмет {self.name} ({self.uid})'


class Subscribe(models.Model):
    """Подписка."""

    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Атлет',
    )
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Тренер',
    )

    class Meta:
        constraints = (models.UniqueConstraint(fields=['athlete', 'coach'], name='unique_athlete_coach'),)

    def __str__(self) -> str:
        return f'Подписка атлета {self.athlete_id} на тренера {self.coach_id}'
