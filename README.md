[![Build Status](https://travis-ci.org/botswana-harvard/edc-death-report.svg)](https://travis-ci.org/botswana-harvard/edc-death-report)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-death-report/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-death-report?branch=develop)
[![Coverage Status](https://coveralls.io/repos/github/Botswana-Havard-Edc-Repos/edc-death-report/badge.svg?branch=develop)](https://coveralls.io/github/Botswana-Havard-Edc-Repos/edc-death-report?branch=develop)

# edc-death-report


A death report model class is declared in your app just like any other CRF:

	from django.db import models
	from edc_base.model.models import BaseUuidModel
	from simple_history.models import HistoricalRecords as AuditTrail
	from edc_death_report.models import DeathReportModelMixin
	from edc_metadata.managers import CrfMetaDataManager
	from edc_visit_tracking.models import CrfModelMixin
	
	from .subject_visit import SubjectVisit	
	
	class SubjectDeathReport(CrfModelMixin, DeathReportModelMixin, BaseUuidModel):
	
	    """ A model completed by the user on the subject's death. """
		
	    subject_visit = models.OneToOneField(SubjectVisit)
	
	    history = AuditTrail()
	
	    entry_meta_data_manager = CrfMetaDataManager(MaternalVisit)
	
	    class Meta:
	        app_label = 'my_app'
	        verbose_name = "Subject Death Report"


The ModelForm mixin `DeathReportFormMixin` is included and does some basic validation.

Admin classes for the models related to the death report via the `DeathReportModelMixin` are registered via the `admin` module.
