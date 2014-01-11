import csv
import StringIO
from django.test import TestCase
from django.test.client import RequestFactory
from cbvtoolkit.views import CSVDownloadView


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
