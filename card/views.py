from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from multi_form_view import MultiModelFormView

from .models import Deck, Card
from .forms import DeckForm, CardForm, ImageForm


def error_404_view(request, exception):
    return render(request, '404.html')


def error_403_view(request, exception):
    return render(request, '403.html')


def home(request):
    return render(request, 'base.html')


class DeckListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'deck_list.html'
    context_object_name = 'decks'
    login_url = '/login/'
    redirect_field_name = 'login'

    def get_queryset(self):
        return Deck.objects.filter(author=self.request.user)

    def test_func(self):
        if self.get_queryset():
            return self.request.user == self.get_queryset().first().author
        return False


class DeckDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Deck
    template_name = 'deck_detail.html'
    context_object_name = 'deck'
    login_url = '/login/'
    redirect_field_name = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cards_qty'] = len(Card.objects.filter(deck=self.object))
        context['mastered_questions'] = len(Card.objects.filter(deck=self.object).filter(status='MASTERED'))
        return context

    def test_func(self):
        return self.request.user == self.get_object().author


def next_card(request, deck_pk, i):
    if request.method == 'POST':
        card = Card.objects.get(id=request.POST['cardId'])
        if 'markAsLearned' in request.POST:
            card.mark_as_learned()
        else:
            card.mark_as_not_learned()
    if i < int(request.POST['cardQty']):
        return redirect('question-detail', deck_pk, i + 1)
    else:
        return redirect('deck-detail', deck_pk)


class QuestionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Card
    template_name = 'card_question.html'
    context_object_name = 'card'
    login_url = '/login/'
    redirect_field_name = 'login'

    def get_object(self, queryset=None):
        try:
            deck_pk = self.kwargs['deck_pk']
            i = self.kwargs['i']
            return Card.objects.filter(deck__id=deck_pk)[i-1]
        except IndexError:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_no'] = self.kwargs['i']
        return context

    def test_func(self):
        return self.request.user == self.get_object().deck.author


class AnswerDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Card
    template_name = 'card_answer.html'
    context_object_name = 'card'
    login_url = '/login/'
    redirect_field_name = 'login'

    def get_object(self, queryset=None):
        try:
            deck_pk = self.kwargs['deck_pk']
            i = self.kwargs['i']
            return Card.objects.filter(deck__id=deck_pk)[i-1]
        except IndexError:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_no'] = self.kwargs['i']
        context['next_card_no'] = self.kwargs['i']+1
        context['deck_pk'] = self.kwargs['deck_pk']
        context['cards_qty'] = len(Card.objects.filter(deck__id=self.kwargs['deck_pk']))
        return context

    def test_func(self):
        return self.request.user == self.get_object().deck.author


class DeckCreateView(CreateView):
    form_class = DeckForm
    template_name = 'form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class DeckUpdateView(UpdateView):
    model = Deck
    form_class = DeckForm
    template_name = 'form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class DeckDeleteView(DeleteView):
    model = Deck
    template_name = 'deck_confirm_delete.html'
    success_url = reverse_lazy('deck-list')


class CardCreateView(MultiModelFormView):
    form_classes = {
        'card_form': CardForm,
        # 'deck_form': DeckForm,
        'question_image_form': ImageForm,
        'answer_image_form': ImageForm,
    }
    # record_id = None
    template_name = 'add_card_form.html'

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




