import csv
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin


class CSVDownloadView(View):
    """
    Initializes download on GET request.  Must Implement `get_csv_data`
    """
    @property
    def columns(self):
        raise NotImplementedError('Must define columns as tuple')

    @property
    def filename(self):
        raise NotImplementedError('Must declare filename')

    def build_response(self, csv_data):
        """
        Constructs a response using csv.writer.
        """
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(self.columns)
        for line in csv_data:
            writer.writerow([line[name] for name in self.columns])
        return response

    def get_csv_data(self):
        """
        Must return an iterable of dictionaries.  Will create csv by iterating through
        what is returned from this function and applying 'columns' to it.
        """
        raise NotImplementedError('Must Define get_csv_data')

    def get(self, request):
        response = self.build_response(self.get_csv_data()) 
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)
        return response


class MultiFormView(ContextMixin, TemplateResponseMixin, View):
    """
    Supports rendering and processing multiple different forms through the same url.
    """
    @property
    def forms(self):
        """
        Contains all the form classes to instantiate, must be a collection.
        """
        raise NotImplementedError()

    def build_forms(self, **kwargs):
        """
        Returns a dictionary of forms, keyed by form class name lowercased.
        """
        forms = {}
        # loop through all the forms and see any were provided in kwargs
        # if they were that means it is a bound form, if not instantiate a new form
        for form_name, form_class in self._forms_dict.items():
            if form_name in kwargs:
                forms[form_name] = kwargs[form_name]
            else:
                forms[form_name] = self._get_form_instance(form_name)
        return forms

    def dispatch(self, request, *args, **kwargs):
        """
        Converts the `forms` collection into a dictionary with string keys that can
        be used to reference the form classes.
        """
        self._build_form_map()
        return super(MultiFormView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data()) 

    def get_context_data(self, **kwargs):
        context = super(MultiFormView, self).get_context_data(**kwargs)
        context['forms'] = self.build_forms(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        """
        Processes a single form, requires a form identifier in the params named `form_name`.
        """
        form_name = request.POST.get('form_name')
        if form_name not in self._forms_dict:
            return HttpResponseForbidden()

        form = self._forms_dict[form_name](request.POST)
        if form.is_valid():
            return self._form_valid(form_name, form)
        else:
            kwargs = {
                form_name: form,
            }
            return self.render_to_response(self.get_context_data(**kwargs)) 

    def _build_form_map(self):
        """
        Takes a collection a form classes and creates a mapping of class name strings
        to the classes.
        @return void - sets the attribute `_forms_dict`
        """
        self._forms_dict = dict((form.__name__.lower(), form) for form in self.forms)

    def _form_valid(self, form_name, form):
        """
        Delegates the form to the correct form_<<form_name>>_valid method
        @param form_name string
        @param form Object 
        """
        method_name = '{}_valid'.format(form_name)
        getattr(self, method_name)(form)
        return HttpResponseRedirect(self._get_success_url(form_name))

    def _get_success_url(self, form_name):
        """
        Checks to see if there is a specific success_url method defined for this form
        if not defaults to `self.success_url`
        @return string
        """
        method_name = 'get_{}_success_url'.format(form_name)
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        else:
            return self.success_url

    def _get_form_instance(self, form_name):
        """
        Instantiates a form.  Looks for a user-defined method to do it, else it just
        instantiates a form with no args.
        """
        method_name = 'get_{}_instance'.format(form_name)
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        else:
            return self._forms_dict[form_name]()
