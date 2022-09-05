from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.validators import validate_username


class User(AbstractUser):
    ADMIN = "admin"
    USER = "user"
    USER_CHOICES = [
        (ADMIN, _("admin")),
        (USER, _("user")),
    ]
    username = models.CharField(
        _("username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and "
            "@/./+/-/_ only."
        ),
        validators=[
            validators.RegexValidator(
                r"^[\w.@+-]+$",
                _(
                    "Enter a valid username. "
                    "This value may contain only letters, numbers "
                    "and @/./+/-/_ characters."
                ),
                "invalid",
            ),
            validate_username,
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    role = models.CharField(max_length=9, choices=USER_CHOICES, default=USER)

    email = models.EmailField(
        unique=True
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def is_admin(self):
        if self.role == "admin":
            return True
        return False


class AnonymousUserExtraFields(AnonymousUser):
    def is_admin(self):
        return False


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_author',
        verbose_name='Автор контента',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f' Подписки {self.subscriber}'
