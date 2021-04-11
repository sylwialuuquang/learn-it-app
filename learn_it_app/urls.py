from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from card.views import DeckListView, DeckDetailView, home, DeckCreateView, \
    DeckUpdateView, DeckDeleteView, CardCreateView, next_card, CardListVIew, CardDeleteView, CardUpdateView, \
    QACardView, next_red_card

# admin.site.register(Image)
# admin.site.register(Deck)
# admin.site.register(Card)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('decks/', DeckListView.as_view(), name='deck-list'),
    path('deck/create/', DeckCreateView.as_view(), name='deck-create'),
    path('deck/update/<int:pk>/', DeckUpdateView.as_view(), name='deck-update'),
    path('deck/delete/<int:pk>/', DeckDeleteView.as_view(), name='deck-delete'),
    path('deck/<int:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('deck/<int:deck_pk>/card/<int:index>/', QACardView.as_view(), name='card'),
    path('deck/<int:pk>/cards/', CardListVIew.as_view(), name='card-list'),
    path('deck/<int:pk>/add_card/', CardCreateView.as_view(), name="add-card"),
    path('deck/<int:deck_pk>/update_card/<int:pk>', CardUpdateView.as_view(), name="card-update"),
    path('deck/<int:deck_pk>/delete_card/<int:pk>', CardDeleteView.as_view(), name="card-delete"),
    path('deck/<int:deck_pk>/question/<int:i>/next', next_card, name='next-card'),
    path('deck/<int:deck_pk>/question/<int:i>/next-red', next_red_card, name='next-red-card'),
    path('accounts/', include('accounts.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'card.views.error_404_view'
handler403 = 'card.views.error_403_view'
