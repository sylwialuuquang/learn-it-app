from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from multi_form_view import MultiModelFormView

from .models import Deck, Card, Image
from .forms import DeckForm, CardForm, ImageForm


def error_404_view(request, exception):
    return render(request, '404.html')


def error_403_view(request, exception):
    return render(request, '403.html')


def home(request):
    return render(request, 'home.html')


def next_card(request, deck_pk, i):
    if request.method == 'POST':
        card = Card.objects.get(id=request.POST['cardId'])
        if request.POST['markAsLearned'] != request.POST['markAsLearnedInit']:
            if request.POST['markAsLearned'] == "MASTERED":
                card.mark_as_learned()
            else:
                card.mark_as_not_learned()
    if i < int(request.POST['cardQty']):
        return redirect('card', deck_pk, i + 1)
    else:
        return redirect('deck-detail', deck_pk)


def next_red_card(request, deck_pk, i):
    if request.method == 'POST':
        card = Card.objects.get(id=request.POST['cardId'])
        if request.POST['markAsLearned'] != request.POST['markAsLearnedInit']:
            if request.POST['markAsLearned'] == "MASTERED":
                card.mark_as_learned()
            else:
                card.mark_as_not_learned()
        if i < int(request.POST['cardQty']):
            index = Deck.next_red_card_index(deck_pk, i)
            return redirect('card', deck_pk, index)
        else:
            return redirect('deck-detail', deck_pk)


class QACardView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Card
    template_name = 'card.html'
    context_object_name = 'card'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_object(self, queryset=None):
        try:
            deck_pk = self.kwargs['deck_pk']
            i = self.kwargs['index']
            return Card.objects.filter(deck__id=deck_pk)[i-1]
        except IndexError:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_no'] = self.kwargs['index']
        context['next_card_no'] = self.kwargs['index']+1
        context['deck_pk'] = self.kwargs['deck_pk']
        context['cards_qty'] = len(Card.objects.filter(deck__id=self.kwargs['deck_pk']))
        context['next_red'] = Deck.next_red_card_index(self.kwargs['deck_pk'], self.kwargs['index'])
        return context

    def test_func(self):
        return self.request.user == self.get_object().deck.author


class DeckListView(LoginRequiredMixin, ListView):
    template_name = 'deck_list.html'
    context_object_name = 'decks'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_queryset(self):
        return Deck.objects.filter(author=self.request.user)


class DeckDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Deck
    template_name = 'deck_detail.html'
    context_object_name = 'deck'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cards_qty'] = len(Card.objects.filter(deck=self.object))
        context['mastered_questions'] = len(Card.objects.filter(deck=self.object).filter(status='MASTERED'))
        return context

    def test_func(self):
        return self.request.user == self.get_object().author


class CardListVIew(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'card_list.html'
    context_object_name = 'cards'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_queryset(self):
        return Card.objects.filter(deck__id=self.kwargs['pk'])

    def test_func(self):
        try:
            return self.request.user == Deck.objects.get(id=self.kwargs['pk']).author
        except ObjectDoesNotExist:
            raise Http404()


class DeckCreateView(LoginRequiredMixin, MultiModelFormView):
    form_classes = {
        'deck_form': DeckForm,
        'img_form': ImageForm
    }
    template_name = 'add_deck_form.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['deck_form']['user'] = self.request.user
        kwargs['deck_form']['prefix'] = 'deck'
        kwargs['img_form']['prefix'] = 'img'
        return kwargs

    def get_objects(self):
        self.deck_id = self.kwargs.get('deck_id', None)
        try:
            deck = Deck.objects.get(id=self.deck_id)
        except ObjectDoesNotExist:
            deck = None
        return {
            'deck_form': deck,
            'img_form': deck.img if deck else None
        }

    def get_success_url(self):
        return reverse('deck-list')

    def forms_valid(self, forms):
        deck = forms['deck_form'].save(commit=False)
        if forms['img_form'].instance.img:
            deck.img = forms['img_form'].save()
        deck.save()
        return super(DeckCreateView, self).forms_valid(forms)


class DeckUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Deck
    form_class = DeckForm
    template_name = 'deck_update_form.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        tmp = super().post(request, **kwargs)
        if 'new_deck_img' in request.FILES:
            deck_img = Image(img=request.FILES['new_deck_img'])
            deck_img.save()
            self.object.update_img(deck_img)
        return tmp

    def test_func(self):
        try:
            return self.request.user == Deck.objects.get(id=self.kwargs['pk']).author
        except ObjectDoesNotExist:
            raise Http404()


class DeckDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Deck
    template_name = 'deck_confirm_delete.html'
    success_url = reverse_lazy('deck-list')
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def test_func(self):
        print(self.request.user)
        print(Deck.objects.get(id=self.kwargs['pk']).author)
        try:
            return self.request.user == Deck.objects.get(id=self.kwargs['pk']).author
        except ObjectDoesNotExist:
            raise Http404()


class CardCreateView(LoginRequiredMixin, UserPassesTestMixin, MultiModelFormView):
    form_classes = {
        'card_form': CardForm,
        'question_image_form': ImageForm,
        'answer_image_form': ImageForm,
    }
    template_name = 'add_card_form.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['card_form']['prefix'] = 'card'
        kwargs['card_form']['deck_id'] = self.kwargs['pk']
        kwargs['question_image_form']['prefix'] = 'question_image'
        kwargs['answer_image_form']['prefix'] = 'answer_image'
        return kwargs

    def get_objects(self):
        self.card_id = self.kwargs.get('card_id', None)
        try:
            card = Card.objects.get(id=self.card_id)
        except ObjectDoesNotExist:
            card = None
        return {
            'card_form': card,
            'question_image_form': card.question_img if card else None,
            'answer_image_form': card.answer_img if card else None,
        }

    def get_success_url(self):
        return reverse('deck-list')

    def forms_valid(self, forms):
        card = forms['card_form'].save(commit=False)
        if forms['question_image_form'].instance.img:
            card.question_img = forms['question_image_form'].save()
        if forms['answer_image_form'].instance.img:
            card.answer_img = forms['answer_image_form'].save()
        card.save()
        return super(CardCreateView, self).forms_valid(forms)

    def test_func(self):
        try:
            return self.request.user == Deck.objects.get(id=self.kwargs['pk']).author
        except ObjectDoesNotExist:
            raise Http404()


class CardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'card_update_form.html'
    success_url = reverse_lazy('deck-list')
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['deck_id'] = self.kwargs['deck_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = Card.objects.get(id=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        tmp = super().post(request, **kwargs)
        if 'new_question_image' in request.FILES:
            question_img = Image(img=request.FILES['new_question_image'])
            question_img.save()
            self.object.update_question_img(question_img)
        if 'new_answer_image' in request.FILES:
            answer_img = Image(img=request.FILES['new_answer_image'])
            answer_img.save()
            self.object.update_answer_img(answer_img)
        return tmp

    def test_func(self):
        try:
            return self.request.user == Deck.objects.get(id=self.kwargs['deck_pk']).author
        except ObjectDoesNotExist:
            raise Http404()


class CardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Card
    template_name = 'card_confirm_delete.html'
    success_url = reverse_lazy('deck-list')
    login_url = '/accounts/login/'
    redirect_field_name = 'login'

    def test_func(self):
        try:
            return self.request.user == Deck.objects.get(id=self.kwargs['deck_pk']).author
        except ObjectDoesNotExist:
            raise Http404()

