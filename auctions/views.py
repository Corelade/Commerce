from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        'auction_listings': AuctionListings.objects.filter(is_closed=False)
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
    price = forms.IntegerField(min_value=0)


def create_listing(request):
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            item_name = form.cleaned_data['item_name']
            category = form.cleaned_data['category']
            image = form.cleaned_data['image']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            category = Category(category=category)
            category.save()
            listing = AuctionListings(user=request.user, item_name=item_name, description=description,
                                      price=price, category=category, image=image)
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

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))


def listing_page(request, name):
    item = AuctionListings.objects.get(item_name=name)
    item_name = item.item_name
    watchlist_content = [item.item_name.item_name for item in Watchlist.objects.all()]
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            new_bid = form.cleaned_data['place_bid']
            try:
                bid = Bid.objects.get(auction_listing_id=item.id)
                if new_bid > bid.new_bid:
                    bid.new_bid = new_bid
                    bid.save()
                    return HttpResponseRedirect(reverse(listing_page, args=[name]))
                else:
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'watchlist': 'Add To Watchlist',
                        'form': BidForm(request.POST),
                        'message': 'Bid must be higher than previous bid'
                    })
            except:
                if new_bid > item.price:
                    new_bid = Bid(user=request.user, auction_listing=item, new_bid=new_bid)
                    new_bid.save()
                    return HttpResponseRedirect(reverse(listing_page, args=[name]))
                else:
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'watchlist': 'Add To Watchlist',
                        'form': BidForm(request.POST),
                        'message': 'Bid must be higher than price'
                    })
    else:
        if item.is_closed is False:
            if request.user.id == item.user_id:
                try:
                    new_bid = Bid.objects.get(auction_listing_id=item.id)
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'close': 'Close',
                        'current_bid': new_bid.new_bid,
                        'comment_form': CommentForm(),
                        'comments': Comment.objects.filter(auction_listing_id=item.id)
                    })
                except:
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'close': 'Close',
                        'comment_form': CommentForm(),
                        'comments': Comment.objects.filter(auction_listing_id=item.id)
                    })
            else:
                try:
                    new_bid = Bid.objects.get(auction_listing_id=item.id)
                    form = BidForm(initial={'place_bid': new_bid.new_bid + 1})
                    if item_name not in watchlist_content:
                        return render(request, 'auctions/listing_page.html', {
                            'name': name,
                            'item': item,
                            'watchlist': 'Add To Watchlist',
                            'current_bid': new_bid.new_bid,
                            'form': form,
                            'comment_form': CommentForm(),
                            'comments': Comment.objects.filter(auction_listing_id=item.id)
                        })
                    else:
                        return render(request, 'auctions/listing_page.html', {
                            'name': name,
                            'item': item,
                            'remove': 'Remove From Watchlist',
                            'current_bid': new_bid.new_bid,
                            'form': form,
                            'comment_form': CommentForm(),
                            'comments': Comment.objects.filter(auction_listing_id=item.id)
                        })

                except:
                    form = BidForm(initial={'place_bid': item.price + 1})
                    if item_name not in watchlist_content:
                        return render(request, 'auctions/listing_page.html', {
                            'name': name,
                            'item': item,
                            'watchlist': 'Add To Watchlist',
                            'form': form,
                            'comment_form': CommentForm(),
                            'comments': Comment.objects.filter(auction_listing_id=item.id)
                        })
                    else:
                        return render(request, 'auctions/listing_page.html', {
                            'name': name,
                            'item': item,
                            'remove': 'Remove From Watchlist',
                            'form': form,
                            'comment_form': CommentForm(),
                            'comments': Comment.objects.filter(auction_listing_id=item.id)
                        })
        else:
            new_bid = Bid.objects.get(auction_listing_id=item.id)
            if request.user.id == item.user_id:
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'message': "You've closed this auction",
                    'current_bid': new_bid.new_bid,
                    'comment_form': CommentForm()
                })
            elif request.user.id == new_bid.user_id:
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'current_bid': new_bid.new_bid,
                    'message': "Congratulations!!! You won this auction!",
                    'comment_form': CommentForm()
                })
            else:
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'current_bid': new_bid.new_bid,
                    'message': 'This auction has been closed',
                    'comment_form': CommentForm()
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


def close(request, name):
    item = AuctionListings.objects.get(item_name=name)
    item.is_closed = True
    item.save()
    return HttpResponseRedirect(reverse(listing_page, args=[name]))


def comment(request, name):
    item = AuctionListings.objects.get(item_name=name)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            comment = Comment(user=request.user, auction_listing_id=item.id, comment=comment)
            comment.save()
            return HttpResponseRedirect(reverse(listing_page, args=[name]))
        else:
            new_bid = Bid.objects.get(auction_listing_id=item.id)
            return render(request, 'auctions/listing_page.html', {
                'name': name,
                'item': item,
                'current_bid': new_bid.new_bid,
                'comment_form': CommentForm(),
            })

def watchlist(request):
    pass
