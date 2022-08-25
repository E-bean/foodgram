from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True)
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1), ],
    )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)  # HEX код
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта',
        help_text='Введите описание рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True,
        help_text='Загрузите картинку'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления',
        validators=[MinValueValidator(1), ],
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    favorite_count = models.PositiveIntegerField(
        verbose_name='Число добавлений в избранное'
    )

    def __str__(self):
        return self.name
