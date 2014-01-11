django-cbv-toolkit
==================

More Class Based Views for common uses

## CSVDownloadView

Provides a simple CBV interface to creating views that allow data to be downloaded as CSV.

### Usage:
- subclass CSVDownloadView
- define `columns` which is a tuple of strings, (columns will appear in this order)
- define `filename` string the name of the file to be downloaded
- define `get_csv_data` instace method return an iterable of dictionaries

### Example: 

from cbvtoolkit.views import CSVDownloadView

MyCSVDownloadView(CSVDownloadView):
    columns = ('name', 'age')
    filename = 'yourfile.csv'

    def get_csv_data(self):
        """
        Generates 10 random dictionaries, using the keys specified in keys.
        @return must return iterable of dictionaries
        """
        for i in range(10):
            yield dict((column, str(i)) for column in self.columns) 
