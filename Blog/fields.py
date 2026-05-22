from django.db import models


class SummernoteTextField(models.TextField):
    def to_python(self, value):
        if value in self.empty_values:
            return ""
        return str(value)