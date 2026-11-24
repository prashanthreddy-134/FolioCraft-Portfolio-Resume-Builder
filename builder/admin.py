from django.contrib import admin
from .models import *
admin.site.register([Profile,PortfolioTemplate,Portfolio,Skill,Project,Experience,Education,Certification,Testimonial,PortfolioView])
