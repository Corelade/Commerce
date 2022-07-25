from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<str:name>", views.listing_page, name="listing_page"),
    path("<str:name>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("<str:name>/remove", views.remove, name="remove"),
    path("<str:name>/close", views.close, name="close"),
]
