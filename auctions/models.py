from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username


class AuctionListings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)
    price = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.item_name


class Category(models.Model):
    category = models.CharField(max_length=30)

    def __str__(self):
        return self.category


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)

    def __str__(self):
        return self.item_name.item_name


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)
    new_bid = models.IntegerField()  # default=0)

    def __str__(self):
        return self.new_bid

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commented')
    auction_listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.comment

