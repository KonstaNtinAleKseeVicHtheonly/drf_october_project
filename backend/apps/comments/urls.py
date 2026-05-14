from apps.comments import views
from django.urls import path

app_name = 'all_comments'

urlpatterns = [
    
    path('', views.CommentListCreateView.as_view(), name='comment-list'),
    path('<int:pk>/',  views.CommentDetailView.as_view(), name='comment-detail'),
    path('my-comments/', views.MyCommentsView.as_view(), name='my-comments'),
    path('post/<int:post_id>/', views.post_comments, name='post-comments'),
    path('comment-replies/<int:comment_id>/', views.comment_replies, name='comment-replies')#если не будет работать то прописать url : '<int:comment_id>/replies/'
    ]
