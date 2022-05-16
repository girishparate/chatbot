from django.db import models

# Create your models here.
class Question(models.Model):
    user_question = models.TextField()

    def __str__(self):
        return str(self.user_question)

class Answer(models.Model):
    MARK = [['Right','Right'],['Wrong','Wrong']]
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    mark = models.CharField(max_length=30, blank=True, null=True, choices=MARK)

    def __str__(self):
        return str(self.answer)
