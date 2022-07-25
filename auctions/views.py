from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        'auction_listings': AuctionListings.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class CreateForm(forms.Form):
    item_name = forms.CharField(max_length=30)
    category = forms.CharField(max_length=30)
    image = forms.ImageField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    starting_bid = forms.IntegerField(min_value=0)


def create_listing(request):
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            item_name = form.cleaned_data['item_name']
            category = form.cleaned_data['category']
            image = form.cleaned_data['image']
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['starting_bid']
            category = Category(category=category)
            category.save()
            listing = AuctionListings(user=request.user, item_name=item_name, description=description,
                                      starting_bid=starting_bid, category=category, image=image)
            listing.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return render(request, 'auctions/create_listing.html', {
                'form': CreateForm(request.POST)
            })

    return render(request, 'auctions/create_listing.html', {
        'form': CreateForm()
    })


class BidForm(forms.Form):
    place_bid = forms.IntegerField(min_value=0)


def listing_page(request, name):
    item = AuctionListings.objects.get(item_name=name)
    item_name = item.item_name
    watchlist_content = [item.item_name.item_name for item in Watchlist.objects.all()]
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            new_bid = form.cleaned_data['place_bid']
            if new_bid > item.price:
                new_bid = Bid(user=request.user, auction_listing=item, new_bid=new_bid)
                new_bid.save()
                return HttpResponseRedirect(reverse(listing_page, args=[name]))
            else:
                if item_name not in watchlist_content:
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'watchlist': 'Add To Watchlist',
                        'form': BidForm(request.POST),
                        'message': 'Bid must be higher than previous bid'
                    })
                else:
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'remove': 'Remove From Watchlist',
                        'form': BidForm(request.POST),
                        'message': 'Bid must be higher than previous bid'
                    })

    else:
        if request.user.id == item.user_id:
            return render(request, 'auctions/listing_page.html', {
                'name': name,
                'item': item,
                'close': 'Close'
            })
        else:
            form = BidForm(initial={'place_bid': item.price + 1})
            if item_name not in watchlist_content:
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'watchlist': 'Add To Watchlist',
                    'form': form
                })
            else:
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'remove': 'Remove From Watchlist',
                    'form': form
                })


def add_to_watchlist(request, name):
    item = AuctionListings.objects.get(item_name=name)
    item_name = item.item_name
    watchlist_content = [item.item_name.item_name for item in Watchlist.objects.all()]
    if item_name not in watchlist_content:
        saved_item = Watchlist(user=request.user, item_name=item)
        saved_item.save()
    return HttpResponseRedirect(reverse(listing_page, args=[name]))


def remove(request, name):
    item = AuctionListings.objects.get(item_name=name)
    item_id = item.id
    Watchlist.objects.get(item_name_id=item_id).delete()
    return HttpResponseRedirect(reverse(listing_page, args=[name]))
    # I might need to refine this. Firstly, i want to add a 'is_closed' field to the Watchlist model so if
    # any saved_item has been deleted, it wont show on the watchlist but will still be saved in the database
