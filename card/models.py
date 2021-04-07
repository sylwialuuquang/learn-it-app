from django.db.models import Model, CharField, ForeignKey, CASCADE, TextField, TextChoices, ImageField, DO_NOTHING
from django.contrib.auth.models import User
from django.urls import reverse


class Image(Model):
    img = ImageField(upload_to='images')

    def __str__(self):
        return self.img.name


class Deck(Model):
    name = CharField(max_length=128)
    author = ForeignKey(User, on_delete=CASCADE, related_name='author')
    img = ForeignKey(Image, on_delete=CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('deck-detail', args=[str(self.id)])


class Card(Model):

    class QuestionStatus(TextChoices):
        MASTERED = 'MASTERED'
        LEARNING = 'LEARNING'

    deck = ForeignKey(Deck, on_delete=CASCADE)
    question = TextField()
    question_img = ForeignKey(Image, on_delete=DO_NOTHING, related_name='question', null=True, blank=True)
    answer = TextField()
    answer_img = ForeignKey(Image, on_delete=DO_NOTHING, related_name='answer', null=True, blank=True)
    status = CharField(
        max_length=24,
        choices=QuestionStatus.choices,
        default=QuestionStatus.LEARNING
    )

    def __str__(self):
        return self.question

    def mark_as_learned(self):
        self.status = "MASTERED"
        self.save()

    def mark_as_not_learned(self):
        self.status = "LEARNING"
        self.save()
