from django.db import models

class Task(models.Model):
    TASK_TYPES = [
        ('self_help', 'Self-help Coach'),
        ('text_task', 'Text Task'),
        ('mindfulness', 'Mindfulness and Gratitude'),
        ('brain_train', 'Brain-train'),
    ]

    user_id = models.IntegerField()
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    task_content = models.TextField()
    user_response = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.task_type} - {self.timestamp}"
