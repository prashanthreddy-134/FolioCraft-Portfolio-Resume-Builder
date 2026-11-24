from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
class RegisterForm(UserCreationForm):
    email=forms.EmailField()
    class Meta: model=User; fields=("username","email","password1","password2")
class ProfileForm(forms.ModelForm):
    class Meta: model=Profile; exclude=("user",)
class PortfolioForm(forms.ModelForm):
    class Meta: model=Portfolio; fields=("title","template","is_public")
class SkillForm(forms.ModelForm):
    class Meta: model=Skill; fields=("name","proficiency","category")
class ProjectForm(forms.ModelForm):
    class Meta: model=Project; fields=("title","description","image","tech_stack","github_url","live_url","featured")
class ExperienceForm(forms.ModelForm):
    class Meta: model=Experience; fields=("company","position","location","start_date","end_date","current","description")
    start_date=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    end_date=forms.DateField(required=False,widget=forms.DateInput(attrs={"type":"date"}))
class EducationForm(forms.ModelForm):
    class Meta: model=Education; fields=("institution","degree","field","start_date","end_date","description")
    start_date=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    end_date=forms.DateField(required=False,widget=forms.DateInput(attrs={"type":"date"}))
class CertificationForm(forms.ModelForm):
    class Meta: model=Certification; fields=("name","issuer","issue_date","credential_url")
    issue_date=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
class TestimonialForm(forms.ModelForm):
    class Meta: model=Testimonial; fields=("author","role","content")
