django-cbv-toolkit
==================

More Class Based Views for common uses

# CSVDownloadView

Provides a simple CBV interface to creating views that allow data to be downloaded as CSV.
Often find that I need to create views to allow user to download a CSV.  This provides an
OOP way of doing that using django's built in CBVs.

### Usage:
- subclass `CSVDownloadView`
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

--------

# MultiFormView

Allows one view to render and validate multiple different form classes.  Sometimes it is required that a single view has different forms on it.  I didn't see an easy built in way to do this so MultiFormView was created to assist with the task.


### Usage:
- subclass 'MultiFormView'
- define class property 'forms' which should be a tuple of Form classes
- Each class method will reference the forms by the `class.__name__.lower`, so `MyTestForm` will be referenced by methods as `mytestform`.
