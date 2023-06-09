"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from money import views
from users import views as user_views
from django.contrib.auth import views as authentication_views
from django.conf.urls.static import static
from django.conf import settings
 
app_name = 'money'
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.add_income, name='add_income'),
    path('expense/', views.add_expense, name='expense'),
    path('data_analysis/', views.data_analysis, name='data_analysis'),
    path('download-analysis-pdf/', views.download_analysis_pdf, name='download_analysis_pdf'),
    path('user_profile/', user_views.user_profile, name='user_profile'),
    path('register/',user_views.register, name='register'),
    path('login/', authentication_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', authentication_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('edit_profile/', user_views.edit_profile, name='edit_profile'),
    path('about/', views.about, name='about'),
    path('terms-and-privacy/', views.terms_and_privacy, name='terms_and_privacy'),
    path('add_budget/', views.add_budget, name='add_budget'),
    path('view_budgets/', views.view_budgets, name='view_budgets'),
    path('edit_budget/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('delete_budget/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    path('view_bills/', views.view_bills, name='view_bills'),
    path('add_goal/', views.add_goal, name='add_goal'),
    path('view_goals/', views.view_goals, name='view_goals'),
    path('update_goal_progress/<int:goal_id>/', views.update_goal_progress, name='update_goal_progress'),
    path('edit_goal/<int:goal_id>/', views.edit_goal, name='edit_goal'),
    path('delete_goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
