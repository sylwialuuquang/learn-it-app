from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

from card.models import Image, Deck, Card
from card.views import DeckListView, DeckDetailView, QuestionDetailView, AnswerDetailView, home, DeckCreateView, \
    DeckUpdateView, DeckDeleteView, CardCreateView, next_card, CardListVIew, CardDeleteView, CardUpdateView

admin.site.register(Image)
admin.site.register(Deck)
admin.site.register(Card)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('decks/', DeckListView.as_view(), name='deck-list'),
    path('deck/create/', DeckCreateView.as_view(), name='deck-create'),
    path('deck/update/<int:pk>/', DeckUpdateView.as_view(), name='deck-update'),
    path('deck/delete/<int:pk>/', DeckDeleteView.as_view(), name='deck-delete'),
    path('deck/<int:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('deck/<int:pk>/cards/', CardListVIew.as_view(), name='card-list'),
    path('deck/<int:pk>/add_card/', CardCreateView.as_view(), name="add-card"),
    path('deck/<int:deck_pk>/update_card/<int:pk>', CardUpdateView.as_view(), name="card-update"),
    path('deck/<int:deck_pk>/delete_card/<int:pk>', CardDeleteView.as_view(), name="card-delete"),
    path('deck/<int:deck_pk>/question/<int:i>/', QuestionDetailView.as_view(), name='question-detail'),
    path('deck/<int:deck_pk>/question/<int:i>/answer/', AnswerDetailView.as_view(), name='answer-detail'),
    path('deck/<int:deck_pk>/question/<int:i>/next', next_card, name='next-card'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'card.views.error_404_view'
handler403 = 'card.views.error_403_view'
