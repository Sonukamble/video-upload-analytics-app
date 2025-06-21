from django.urls import path
from .views import ChannelSubscribersView, CommentAPIView, CommentDetailAPIView, LikeCountAPIView, LikeVideoAPIView, MySubscriptionsView, SubscribeView, UnsubscribeView, UserLikeListAPIView

urlpatterns = [
    # path('like/', LikeCreate.as_view(), name='like-create'),
    # path('like/<int:pk>/', LikeDetail.as_view(), name='like-detail'),
    path('like/video/<int:video_id>/', LikeVideoAPIView.as_view(), name='like-video'),
    path('likes/count/<int:video_id>/', LikeCountAPIView.as_view(), name='like-count'),
    path('likes/user/', UserLikeListAPIView.as_view(), name='user-likes'),
    
    path('subscribe/<int:channel_id>/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<int:channel_id>/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('subscriptions/me/', MySubscriptionsView.as_view(), name='my-subscriptions'),
    path('subscribers/<int:channelId>/', ChannelSubscribersView.as_view(), name='channel-subscribers'),

    # path('subscriptions/', SubscriptionCreate.as_view(), name='subscription-create'),
    # path('subscriptions/<int:pk>/', SubscriptionDetail.as_view(), name='subscription-detail'),

    path('comments/', CommentAPIView.as_view()),                 
    path('comments/<uuid:comment_id>/', CommentDetailAPIView.as_view()),  # DELETE specific

]
