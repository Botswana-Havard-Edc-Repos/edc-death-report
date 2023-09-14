from dateutil.relativedelta import relativedelta

from django.test import TestCase

from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO
from edc_death_report.models.reason_hospitalized import ReasonHospitalized

from .models import Cause, CauseCategory, DiagnosisCode, MedicalResponsibility
from .test_models import DeathReportForm, TestDeathVisitModel, DeathReport


class TestDeathReport(TestCase):

    """Broken"""
    def setUp(self):
        if not self.registered_subject.registration_datetime:
            self.registered_subject.registration_datetime = get_utcnow() - relativedelta(weeks=3)
            self.registered_subject.dob = self.test_consent.dob
            self.registered_subject.save()
        test_visit_model = TestDeathVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=get_utcnow())
        self.data = {
            'test_visit_model': test_visit_model.id,
            'comment': None,
            'death_date': get_utcnow().date(),
            'illness_duration': 1,
            'perform_autopsy': NO,
            'cause': Cause.objects.all().first().id,
            'cause_category': CauseCategory.objects.all().first().id,
            'cause_category_other': None,
            'cause_other': None,
            'medical_responsibility': MedicalResponsibility.objects.all().first().id,
            'diagnosis_code': DiagnosisCode.objects.all().first().id,
            'participant_hospitalized': YES,
            'reason_hospitalized': ReasonHospitalized.objects.all().first().id,
            'days_hospitalized': 3,
            'report_datetime': get_utcnow(),
        }

    def test_create_model_instance(self):
        with self.assertRaises(Exception) as cm:
            try:
                test_visit_model = TestDeathVisitModel.objects.get(
                    appointment=self.appointment)
                DeathReport.objects.create(
                    test_visit_model=test_visit_model,
                    report_datetime=get_utcnow(),
                    death_date=(get_utcnow() - relativedelta(weeks=1)).date(),
                    cause=Cause.objects.all().first(),
                    cause_category=CauseCategory.objects.all().first(),
                    diagnosis_code=DiagnosisCode.objects.all().first(),
                    medical_responsibility=MedicalResponsibility.objects.all().first(),
                    illness_duration=1)
            except Exception:
                pass
            else:
                raise Exception(cm.exception)

    def test_form_valid(self):
        form = DeathReportForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_validate_date_of_death_and_registration_datetime(self):
        self.data['death_date'] = (get_utcnow() - relativedelta(weeks=2)).date()
        self.data['participant_hospitalized'] = YES
        self.data['reason_hospitalized'] = ReasonHospitalized.objects.all().first().id
        self.data['days_hospitalized'] = 1
        self.registered_subject.registration_datetime = get_utcnow() - relativedelta(weeks=1)
        self.registered_subject.save()
        form = DeathReportForm(data=self.data)
        form.is_valid()
        self.assertIn(
            'Death date cannot be before date registered', form.errors.get('__all__') or [])

    def test_form_validate_date_of_death_and_dob(self):
        self.data['death_date'] = (get_utcnow() - relativedelta(years=2)).date()
        self.data['participant_hospitalized'] = YES
        self.data['reason_hospitalized'] = ReasonHospitalized.objects.all().first().id
        self.data['days_hospitalized'] = 1
        self.registered_subject.registration_datetime = get_utcnow() - relativedelta(weeks=1)
        self.registered_subject.dob = get_utcnow() - relativedelta(years=1)
        self.registered_subject.save()
        form = DeathReportForm(data=self.data)
        form.is_valid()
        self.assertIn(
            'Death date cannot be before date of birth', form.errors.get('__all__') or [])

    def test_form_not_hospitalized_days_1(self):
        self.data['participant_hospitalized'] = NO
        self.data['reason_hospitalized'] = None
        self.data['days_hospitalized'] = 1
        death_report_form = DeathReportForm(data=self.data)
        self.assertIn(
            'If the participant was not hospitalized, do not indicate for how many days.',
            death_report_form.errors.get('__all__') or [])

    def test_form_not_hospitalized_days_0(self):
        self.data['participant_hospitalized'] = NO
        self.data['reason_hospitalized'] = None
        self.data['days_hospitalized'] = 0
        death_report_form = DeathReportForm(data=self.data)
        self.assertIn(
            'If the participant was not hospitalized, do not indicate for how many days.',
            death_report_form.errors.get('__all__') or [])

    def test_form_reason_hospitalized_days_none(self):
        self.data['participant_hospitalized'] = YES
        self.data['reason_hospitalized'] = ReasonHospitalized.objects.all().first().id
        self.data['days_hospitalized'] = None
        death_report_form = DeathReportForm(data=self.data)
        self.assertIn(
            'If the participant was hospitalized, indicate for how many days.',
            death_report_form.errors.get('__all__') or [])

    def test_form_reason_hospitalized_days0(self):
        self.data['participant_hospitalized'] = YES
        self.data['reason_hospitalized'] = ReasonHospitalized.objects.all().first().id
        self.data['days_hospitalized'] = 0
        death_report_form = DeathReportForm(data=self.data)
        self.assertIn(
            'If the participant was hospitalized, indicate for how many days.',
            death_report_form.errors.get('__all__') or [])

    def test_form_reason_hospitalized_days_neg(self):
        self.data['participant_hospitalized'] = YES
        self.data['reason_hospitalized'] = ReasonHospitalized.objects.all().first().id
        self.data['days_hospitalized'] = -1
        death_report_form = DeathReportForm(data=self.data)
        self.assertIn(
            'If the participant was hospitalized, indicate for how many days.',
            death_report_form.errors.get('__all__') or [])

    def test_form_reason_hospitalized_reason(self):
        self.data['participant_hospitalized'] = YES
        self.data['reason_hospitalized'] = None
        self.data['days_hospitalized'] = 1
        form = DeathReportForm(data=self.data)
        self.assertIn(
            'If the participant was hospitalized, indicate the primary reason.',
            form.errors.get('__all__'))

    def test_form_cause_other(self):
        for cause in Cause.objects.all():
            if 'other' in cause.name.lower():
                self.data['cause'] = cause.id
        form = DeathReportForm(data=self.data)
        self.assertIn(
            'You wrote \'other\' for the cause of death. Please specify.',
            form.errors.get('__all__') or [])

    def test_form_cause_other_specified(self):
        for cause in Cause.objects.all():
            if 'other' in cause.name.lower():
                self.data['cause'] = cause.id
        self.data['cause_other'] = 'an other reason'
        form = DeathReportForm(data=self.data)
        self.assertTrue(form.is_valid())
