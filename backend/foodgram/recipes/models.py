from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_ingredient", fields=["name", "measurement_unit"]
            )
        ]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
    )

    # def __str__(self):
    #     return self.slug


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
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
        upload_to='recipes/images/',
        blank=True,
        help_text='Загрузите картинку'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах',
        validators=[MinValueValidator(1), ],
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes'
    )

    def get_ingredients(self):
        return ",".join([str(i) for i in self.ingredient.all()])

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='amounts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1), ],
    )

    # def __str__(self) -> str:
    #     return self.ingredient


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранные рецепты',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favorite'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f' Избранное {self.user}'
