from django.urls import path
from .views import GenerateTextAPIView, GenerateImagesAPIView, GenerateFinalVideoAPIView, \
    PublishToYoutubeAPIView, GetFinalVideoAPIView, GenerateAudioAPIView, GenerateMusicAPIView, PublishToTikTokAPIView, \
    MusicCallbackAPIView

urlpatterns = [
    path('generate-text/', GenerateTextAPIView.as_view(), name='generate_text'),
    path('generate-audio/', GenerateAudioAPIView.as_view(), name='generate_audio'),
    path('generate-image/', GenerateImagesAPIView.as_view(), name='generate_image'),
    path('generate-video/', GenerateFinalVideoAPIView.as_view(), name='generate_video'),
    path('generate_music/', GenerateMusicAPIView.as_view(), name='generate_music'),
    path('publish-youtube/', PublishToYoutubeAPIView.as_view(), name='publish_youtube'),
    path('publish-tiktok/', PublishToTikTokAPIView.as_view(), name='publish-tiktok'),
    path('videos/<int:video_id>/', GetFinalVideoAPIView.as_view(), name='get_final_video'),
    path("api/music_callback/", MusicCallbackAPIView.as_view(), name="music_callback"),
]
