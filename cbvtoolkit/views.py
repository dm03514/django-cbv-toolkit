import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View


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
