from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Bee
import json
from channels.layers import get_channel_layer