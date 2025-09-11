from django.http import HttpResponse
from attendance.tools.import_metadata import import_metadata


def import_data(request):
    import_metadata()
    return HttpResponse("Import complete")
