from django.urls import path
from .views import (
    upload_pan, verify_pan,
    upload_gst, verify_gst,
    upload_cin, verify_cin
)

urlpatterns = [
    path("upload-pan/", upload_pan),
    path("verify-pan/<str:pan>/", verify_pan),

    path("upload-gst/", upload_gst),
    path("verify-gst/<str:gst>/", verify_gst),

    path("upload-cin/", upload_cin),
    path("verify-cin/<str:cin>/", verify_cin),
]
