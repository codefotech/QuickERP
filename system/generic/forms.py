from django import forms
from system.utils import convert_date_string_to_django_date, convert_time_string_to_django_time
from system.config import _thread_local
from datetime import datetime


class CustomForm(forms.ModelForm):
    created_by = forms.IntegerField(initial=0, required=False)
    updated_by = forms.IntegerField(initial=0, required=False)

    def __init__(self, *args: object, **kwargs: object) -> object:
        super().__init__(*args, **kwargs)
        model = self.Meta.model
        self.data = self.date_time_fields_modify(model, data_dict=self.data)

    def clean(self):
        cleaned_data = super().clean()
        # Perform additional validation here
        return cleaned_data


    @staticmethod
    def date_time_fields_modify(model, data_dict):
        if model and data_dict:
            try:
                for key, value in data_dict.items():
                    if hasattr(model, str(key)):
                        if model._meta.get_field(str(key)).__class__.__name__ == 'DateField':
                            if data_dict.get(str(key)):
                                submitted_date = data_dict.get(str(key))
                                expected_date = convert_date_string_to_django_date(submitted_date)
                                regular_dict = data_dict.copy()
                                regular_dict._mutable = True
                                regular_dict[str(key)] = expected_date
                                regular_dict._mutable = False
                                data_dict = regular_dict
                        elif model._meta.get_field(str(key)).__class__.__name__ == 'TimeField':
                            if data_dict.get(str(key)):
                                submitted_time = data_dict.get(str(key))
                                expected_time = convert_time_string_to_django_time(submitted_time)
                                regular_dict = data_dict.copy()
                                regular_dict._mutable = True
                                regular_dict[str(key)] = expected_time
                                regular_dict._mutable = False
                                data_dict = regular_dict
            except Exception as e:
                print(str(e))
        return data_dict
