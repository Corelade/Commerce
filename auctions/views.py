from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
import string
import random
from .models import *


def index(request):
    return render(request, 'auctions/index.html')


@login_required(login_url='/auctions/login.html')
def home(request):
    return render(request, "auctions/home.html", {
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
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "auctions/register.html")


class CreateForm(forms.Form):
    item_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Item Name'}))
    category = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Category'}))
    price = forms.IntegerField(min_value=0, widget=forms.TextInput(attrs={'placeholder': 'Price'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 30, 'placeholder': 'Description'}))
    image = forms.ImageField(required=False)


@login_required(login_url='/auctions/login.html')
def create_listing(request):
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            item_name = form.cleaned_data['item_name']
            category = form.cleaned_data['category']
            image = form.cleaned_data['image']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            category_list = [category.category for category in Category.objects.all()]
            if category not in category_list:
                category = Category(category=category)
                category.save()
            else:
                category = Category.objects.get(category=category)
            listing = AuctionListings(user=request.user, item_name=item_name, description=description,
                                      price=price, category=category, image=image)
            listing.save()
            return HttpResponseRedirect(reverse(home))
        else:
            return render(request, 'auctions/create_listing.html', {
                'form': CreateForm(request.POST)
            })
    return render(request, 'auctions/create_listing.html', {
        'form': CreateForm()
    })

def transaction_reference():
    str = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10)) 
    return str

class BidForm(forms.Form):
    place_bid = forms.IntegerField(min_value=0, widget=forms.TextInput(attrs={'class': 'form-control'}))


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}))

@login_required(login_url='/auctions/login')
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
                        'message': 'Bid must be higher than previous bid',
                        'comment_form': CommentForm(),
                        'comments': Comment.objects.filter(auction_listing_id=item.id),
                        'users': User.objects.all()
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
                        'message': 'Bid must be higher than price',
                        'comment_form': CommentForm(),
                        'comments': Comment.objects.filter(auction_listing_id=item.id),
                        'users': User.objects.all()
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
                        'comments': Comment.objects.filter(auction_listing_id=item.id),
                        'users': User.objects.all()
                    })
                except:
                    return render(request, 'auctions/listing_page.html', {
                        'name': name,
                        'item': item,
                        'close': 'Close',
                        'comment_form': CommentForm(),
                        'comments': Comment.objects.filter(auction_listing_id=item.id),
                        'users': User.objects.all()
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
                            'comments': Comment.objects.filter(auction_listing_id=item.id),
                            'users': User.objects.all()
                        })
                    else:
                        return render(request, 'auctions/listing_page.html', {
                            'name': name,
                            'item': item,
                            'remove': 'Remove From Watchlist',
                            'current_bid': new_bid.new_bid,
                            'form': form,
                            'comment_form': CommentForm(),
                            'comments': Comment.objects.filter(auction_listing_id=item.id),
                            'users': User.objects.all()
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
                            'comments': Comment.objects.filter(auction_listing_id=item.id),
                            'users': User.objects.all()
                        })
                    else:
                        return render(request, 'auctions/listing_page.html', {
                            'name': name,
                            'item': item,
                            'remove': 'Remove From Watchlist',
                            'form': form,
                            'comment_form': CommentForm(),
                            'comments': Comment.objects.filter(auction_listing_id=item.id),
                            'users': User.objects.all()
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
                reference = transaction_reference()
                try:
                    ref = TransactionReference.objects.get(auctionlistings_id=item.id)
                    ref = ref.trx_ref
                except:
                    ref = TransactionReference(user=request.user, auctionlistings_id=item.id, bid_id=new_bid.id, trx_ref=reference)
                    ref.save()
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'current_bid': new_bid.new_bid,
                    'message': "Congratulations!!! You won this auction!",
                    'success_button': 'Proceed to checkout',
                    'comment_form': CommentForm(),
                    'tx_ref': ref,
                })
            else:
                return render(request, 'auctions/listing_page.html', {
                    'name': name,
                    'item': item,
                    'current_bid': new_bid.new_bid,
                    'message': 'This auction has been closed',
                    'comment_form': CommentForm()
                })

@login_required(login_url='/auctions/login.html')
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

@login_required(login_url='/auctions/login.html')
def watchlist(request):
    return render(request, 'auctions/watchlist.html', {
        'watchlist': Watchlist.objects.filter(user_id=request.user.id)
    })


@login_required(login_url='/auctions/login.html')
def category(request):
    return render(request, 'auctions/category.html', {
        'categories': Category.objects.all()
    }
    
    )
@login_required(login_url='/auctions/login.html')
def category_auctions(request, category):
    category_id = Category.objects.get(category=category).id
    return render(request, 'auctions/category_auctions.html', {
        'category_auctions': AuctionListings.objects.filter(category_id=category_id, is_closed=False),
        'category': category
    })

