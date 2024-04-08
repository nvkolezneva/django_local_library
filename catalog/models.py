from django.db import models

# Create your models here.

from django.urls import reverse  # To generate URLS by reversing URL patterns


class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name = u'Название жанра',
        help_text="Укажите жанр книги (например, научная фантастика, французская поэзия и т.д.)."
    )
    class Meta:
        verbose_name = u'Жанр'
        verbose_name_plural = u'Жанры'

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            unique=True,
                            verbose_name = u'Язык',
                            help_text="Введите язык книги (например, английский, французский, японский и т.д.).")
    class Meta:
        verbose_name = u'Язык'
        verbose_name_plural = u'Языки'
    def get_absolute_url(self):
        """Returns the url to access a particular language instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200, verbose_name = u'Название книги')
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True,verbose_name = u'Автор')
    # Foreign Key used because book can only have one author, but authors can have multiple books.
    # Author as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(
        max_length=1000, help_text="Введите краткое описание книги", verbose_name = u'Краткое содержание')
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 символов <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(
        Genre, help_text="Выберите жанр для этой книги",verbose_name = u'Жанр')
    # ManyToManyField used because a genre can contain many books and a Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True, verbose_name = u'Язык')

    class Meta:
        ordering = ['title', 'author']
        verbose_name = u'Книга'
        verbose_name_plural = u'Книги'

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book record."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title


import uuid  # Required for unique book instances
from datetime import date

from django.conf import settings  # Required to assign User as a borrower


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Уникальный идентификатор для этой конкретной книги во всей библиотеке")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True,verbose_name = u'Книга')
    imprint = models.CharField(max_length=200,verbose_name = u'Сведения о копии')
    due_back = models.DateField(null=True, blank=True,verbose_name = u'Дата возвврата')
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,verbose_name = u'Читатель')

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('d', 'На обслуживание'),
        ('o', 'Зарезервирована пользователем'),
        ('a', 'Доступна'),
        ('r', 'Зарезервирована'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Наличие свободных книг',
        verbose_name = u'Статус')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)
        verbose_name = u'Бронирование книг'
        verbose_name_plural = u'Бронирование книг'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100,verbose_name = u'Имя')
    last_name = models.CharField(max_length=100,verbose_name = u'Фамилия')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name = 'Дата рождения')
    date_of_death = models.DateField(null=True, blank=True, verbose_name = 'Дата смерти')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = u'Автор'
        verbose_name_plural = u'Авторы'

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
