from collaboration.shortcuts import get_project_for_user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from branding.models import BrandProject
from brand_assets.models import BrandAsset
from ai_services.services import AIService
from ai_services.prompts import PromptLibrary
from activitylogs.models import ActivityLog
import json
import os
import requests


@login_required
def generating(request, pk):
    project = get_project_for_user(pk, request.user)
    return render(request, 'branding/generating.html', {'project': project})


@login_required
def results(request, pk):
    project = get_project_for_user(pk, request.user)
    return render(request, 'branding/results.html', {'project': project})


