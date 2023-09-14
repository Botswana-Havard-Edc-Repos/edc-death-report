from django import forms

from edc_constants.constants import YES, NO


class DeathReportFormMixin:

    def clean(self):
        cleaned_data = super(DeathReportFormMixin, self).clean()
        self.validate_report_datetime_and_dob()
        self.validate_death_date_and_dob()
        self.validate_death_date_and_registration()
        self.validate_participant_hospitalized()
        self.validate_other_fields()
        return cleaned_data

    def clean_cause(self):
        cause = self.cleaned_data['cause']
        if not cause:
            raise forms.ValidationError('Indicate the cause of death.')
        return cause

    def validate_other_fields(self):
        cleaned_data = self.cleaned_data
        if 'other' in cleaned_data.get('cause').name.lower() and not cleaned_data.get('cause_other'):
            raise forms.ValidationError('You wrote \'other\' for the cause of death. Please specify.')
        if ('other' in cleaned_data.get('cause_category').name.lower() 
            and not cleaned_data.get('cause_category_other')):
            raise forms.ValidationError(
                'You wrote \'other\' for the cause of death category. Please specify.')
        return cleaned_data

    def validate_participant_hospitalized(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('participant_hospitalized') == YES:
            if not cleaned_data.get('reason_hospitalized'):
                raise forms.ValidationError(
                    'If the participant was hospitalized, indicate '
                    'the primary reason.')
            if not cleaned_data.get('days_hospitalized'):
                raise forms.ValidationError(
                    'If the participant was hospitalized, indicate '
                    'for how many days.')
            if not cleaned_data.get('days_hospitalized') > 0:
                raise forms.ValidationError(
                    'If the participant was hospitalized, indicate '
                    'for how many days.')
        elif cleaned_data.get('participant_hospitalized') == NO:
            if cleaned_data.get('reason_hospitalized'):
                raise forms.ValidationError(
                    'If the participant was not hospitalized, do '
                    'not indicate the primary reason.')
            if cleaned_data.get('days_hospitalized') is not None:
                raise forms.ValidationError(
                    'If the participant was not hospitalized, do '
                    'not indicate for how many days.')

    def validate_death_date_and_registration(self):
        cleaned_data = self.cleaned_data
        registered_subject = cleaned_data.get(self._meta.model.visit_model_attr).appointment.registered_subject
        if cleaned_data.get('death_date') < registered_subject.registration_datetime.date():
            raise forms.ValidationError("Death date cannot be before date registered")

    def validate_death_date_and_dob(self):
        cleaned_data = self.cleaned_data
        registered_subject = cleaned_data.get(self._meta.model.visit_model_attr).appointment.registered_subject
        if cleaned_data.get('death_date') < registered_subject.dob:
            raise forms.ValidationError("Death date cannot be before date of birth")

    def validate_report_datetime_and_dob(self):
        cleaned_data = self.cleaned_data
        registered_subject = cleaned_data.get(self._meta.model.visit_model_attr).appointment.registered_subject
        if cleaned_data.get('report_datetime').date() < registered_subject.dob:
            raise forms.ValidationError("Report date cannot be before date of birth")
