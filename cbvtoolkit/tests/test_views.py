import csv
import StringIO
import unittest
from django import forms
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
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

class MultifFormViewClassSuccessUrl(MultiFormView):
    forms = (EmailForm, UsernameForm)
    success_url = 'class_success_url'

    def emailform_valid(self, form):
        return

class MultifFormViewEmailFormSuccessUrl(MultiFormView):
    forms = (EmailForm, UsernameForm)

    def get_emailform_success_url(self):
        return 'emailform_success_url'

    def emailform_valid(self, form):
        return

class TestMultiFormViewCustomInstantiationMethods(TestMultiFormView):
    def get_emailform_instance(self):
        return Placeholder()

    def get_usernameform_instance(self):
        return Placeholder()

class MultiFormViewIntegrationTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_success(self):
        view = TestMultiFormView.as_view()
        request = self.factory.get('/')
        response = view(request)
        self.assertIn('forms', response.context_data)
        forms = response.context_data['forms']
        self.assertEqual(len(forms), 2)

    def test_get_custom_instantiation_methods(self):
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

    def test_post_form_form_name_not_found(self):
        """
        Tests that when a valid form_name is not found, a 403 is raised.
        """
        view = TestMultiFormView.as_view()
        request = self.factory.post('/', {})
        response = view(request)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_post_form_invalid_form(self):
        """
        Tests that an invalid form can be detected and rerendered as a bound form. And
        that the other forms are instantiated cleanly.
        """
        view = TestMultiFormView.as_view()
        request = self.factory.post('/', {'form_name': 'emailform', 
                                          'email': 'invalid'})
        response = view(request)

        self.assertIn('forms', response.context_data)
        forms = response.context_data['forms']
        self.assertEqual(len(forms), 2)
        self.assertTrue(forms['emailform'].is_bound)

    def test_post_valid_form_redirect_success_url(self):
        """
        Tests that on valid form submission the view will redirect to success_url
        """
        view = MultifFormViewClassSuccessUrl.as_view()
        request = self.factory.post('/', {'form_name': 'emailform', 
                                          'email': 'test@gtest.com'})
        response = view(request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, 'class_success_url')

    def test_post_valid_form_redirect_get_form_success_url(self):
        """
        Tests that on valid form submission the view can call the 
        get_<<form_name>>_success_url method, and redirect to it
        """
        view = MultifFormViewEmailFormSuccessUrl.as_view()
        request = self.factory.post('/', {'form_name': 'emailform', 
                                          'email': 'test@gtest.com'})
        response = view(request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, 'emailform_success_url')

    def test_post_valid_no_form_validmethod_called(self):
        """
        Tests that on a valid form post the `<<form_name>>_valid` method
        is called.
        """
        view = TestMultiFormView.as_view()
        request = self.factory.post('/', {'form_name': 'emailform', 
                                          'email': 'test@gtest.com'})
        with self.assertRaises(AttributeError):
            response = view(request)
