from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import static
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from accounts.views import CustomTokenObtainPair

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('practice/', include('practiceQuestion.urls', namespace='practice_question')),
    path('', include('subject_related.urls', namespace='subject_related')),

    path('edustart_admin/', include('administrator.urls', namespace='edustart_admin')),
    path('edustart_admin/past-question/', include('past_question.urls', namespace='past_question')),

    path('token/obtain/', CustomTokenObtainPair.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    path('schema/', get_schema_view(
        version='v1.0',
        title='Edustart Rest Framework',
        description="None for now"
    ), name='schema'),
    path('docs/', include_docs_urls(
        title='Edustart Rest Framework',
        description="None for now"
    ), name='docs'),

] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
