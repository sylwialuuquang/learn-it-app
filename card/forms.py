from django.forms import ModelForm

from .models import Deck, Card, Image


class DeckForm(ModelForm):
    class Meta:
        model = Deck
        fields = ['name',]

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.author = self.author
        deck = super().save(*args, **kwargs)
        return deck


class CardForm(ModelForm):
    class Meta:
        model = Card
        exclude = ['question_img', 'answer_img', 'deck']

    def __init__(self, *args, **kwargs):
        self.deck = Deck.objects.get(id=kwargs.pop('deck_id'))
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.deck = self.deck
        card = super().save(*args, **kwargs)
        return card


class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['img'].required = False
