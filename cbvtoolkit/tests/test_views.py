import csv
import StringIO
from django import forms
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from cbvtoolkit.views import CSVDownloadView, MultiFormView


class TestCSVDownloadView(CSVDownloadView):
    columns = ('name', 'age', 'height')
    filename = 'test.csv'

    def get_csv_data(self):
        """
        Generates 10 random dictionaries, using the keys specified in keys.
        """
        for i in range(10):
            yield dict((column, str(i)) for column in self.columns) 
        

class CSVDownloadViewIntegrationTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = TestCSVDownloadView.as_view()

    def test_csv_download_view_download_success(self):
        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        # read the returned content, make sure that the headings and the data
        # is present as expected
        f = StringIO.StringIO()
        f.write(response.content)
        f.seek(0)
        reader = csv.reader(f)
        self.assertEqual(list(TestCSVDownloadView.columns), reader.next())
        for i in range(10):
            self.assertEqual([str(i)] * 3, reader.next()) 


class EmailForm(forms.Form):
    email = forms.EmailField()

class UsernameForm(forms.Form):
    username = forms.CharField()

class Placeholder(object): pass

class TestMultiFormView(MultiFormView):
    forms = (EmailForm, UsernameForm)

    def get_template_names(self):
        return ''


class TestMultiFormViewCustomInstantiationMethods(TestMultiFormView):
    def get_emailform_instance(self):
        return Placeholder()

    def get_usernameform_instance(self):
        return Placeholder()

class MultiFormViewIntegrationTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_multi_form_view_get_success(self):
        view = TestMultiFormView.as_view()
        request = self.factory.get('/')
        response = view(request)
        self.assertIn('forms', response.context_data)
        forms = response.context_data['forms']
        self.assertEqual(len(forms), 2)

    def test_multi_form_view_get_custom_instantiation_methods(self):
        """
        Tests that both forms can be instantiated using user-defined methods.
        """
        view = TestMultiFormViewCustomInstantiationMethods.as_view()
        request = self.factory.get('/')
        response = view(request)
        self.assertIn('forms', response.context_data)
        forms = response.context_data['forms']
        self.assertEqual(len(forms), 2)
        for form_instance in forms.values():
            self.assertIsInstance(form_instance, Placeholder)
