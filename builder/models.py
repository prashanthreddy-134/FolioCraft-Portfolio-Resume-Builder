from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    full_name=models.CharField(max_length=100); title=models.CharField(max_length=200,blank=True)
    bio=models.TextField(blank=True); image=models.ImageField(upload_to="profiles/",blank=True,null=True)
    email=models.EmailField(blank=True); phone=models.CharField(max_length=25,blank=True); location=models.CharField(max_length=100,blank=True)
    website=models.URLField(blank=True); github=models.URLField(blank=True); linkedin=models.URLField(blank=True); twitter=models.URLField(blank=True)
    def __str__(self): return self.full_name

class PortfolioTemplate(models.Model):
    name=models.CharField(max_length=100); description=models.TextField(blank=True); active=models.BooleanField(default=True)
    def __str__(self): return self.name

class Portfolio(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="portfolios")
    template=models.ForeignKey(PortfolioTemplate,on_delete=models.SET_NULL,null=True,blank=True)
    title=models.CharField(max_length=180); slug=models.SlugField(unique=True,blank=True)
    is_public=models.BooleanField(default=True); views=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    def save(self,*args,**kwargs):
        if not self.slug: self.slug=f"{slugify(self.title)[:140]}-{uuid.uuid4().hex[:6]}"
        super().save(*args,**kwargs)
    def __str__(self): return self.title

class Skill(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="skills")
    name=models.CharField(max_length=100); proficiency=models.PositiveSmallIntegerField(default=50); category=models.CharField(max_length=50,blank=True)
    def __str__(self): return self.name

class Project(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="projects")
    title=models.CharField(max_length=180); description=models.TextField(); image=models.ImageField(upload_to="projects/",blank=True,null=True)
    tech_stack=models.CharField(max_length=250,blank=True); github_url=models.URLField(blank=True); live_url=models.URLField(blank=True); featured=models.BooleanField(default=False)
    def __str__(self): return self.title

class Experience(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="experiences")
    company=models.CharField(max_length=180); position=models.CharField(max_length=120); location=models.CharField(max_length=100,blank=True)
    start_date=models.DateField(); end_date=models.DateField(null=True,blank=True); current=models.BooleanField(default=False); description=models.TextField()
    def __str__(self): return f"{self.position} at {self.company}"

class Education(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="education")
    institution=models.CharField(max_length=180); degree=models.CharField(max_length=120); field=models.CharField(max_length=120,blank=True)
    start_date=models.DateField(); end_date=models.DateField(null=True,blank=True); description=models.TextField(blank=True)
    def __str__(self): return self.institution

class Certification(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="certifications")
    name=models.CharField(max_length=180); issuer=models.CharField(max_length=180); issue_date=models.DateField(); credential_url=models.URLField(blank=True)
    def __str__(self): return self.name

class Testimonial(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="testimonials")
    author=models.CharField(max_length=100); role=models.CharField(max_length=120,blank=True); content=models.TextField(); approved=models.BooleanField(default=True)
    def __str__(self): return self.author

class PortfolioView(models.Model):
    portfolio=models.ForeignKey(Portfolio,on_delete=models.CASCADE,related_name="view_logs")
    ip_address=models.GenericIPAddressField(null=True,blank=True); viewed_at=models.DateTimeField(auto_now_add=True)
