import os
base_dir = os.path.dirname(os.path.abspath(__file__))

models_data = {
    'activitylogs': 'SystemActivity',
    'audit': 'AuditTrail',
    'monitoring': 'SystemMetric'
}

for app, model in models_data.items():
    models_path = os.path.join(base_dir, 'apps', app, 'models.py')
    content = f"""from django.db import models

class {model}(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f'{model} - {{self.created_at}}'
"""
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(content)
print('Models scaffolded')
