"""coffemachine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""
# Django imports
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('coffemachine.machine.urls', namespace="machine")),
    # enable the admin interface
    url(r'^admin/', admin.site.urls),
]
