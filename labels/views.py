from django.shortcuts import render
import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_pos.wsgi import *
from django_pos import settings
from django.template.loader import get_template
from customers.models import Customer
from products.models import Product
from weasyprint import HTML, CSS

import subprocess
from django.http import JsonResponse
import json

# Create your views here.
@login_required(login_url="/accounts/login/")
def labels_list_view(request):

    return render(request, "labels/labels.html")