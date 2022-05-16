from django.contrib import admin
from .models import *
# Register your models here.
class AnswerAdmin(admin.StackedInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]
    list_display = ['user_question', 'keyword']

admin.site.register(Question, QuestionAdmin)
