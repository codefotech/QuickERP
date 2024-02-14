from django.http import HttpResponse, JsonResponse
from django.views.generic import View

from main.settings import BASE_DIR
from django.shortcuts import render
from django.core.paginator import Paginator


class LogStreamView(View):
    def get(self, request):
        response = HttpResponse(content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'

        # Your log file streaming logic goes here
        with open(f'{BASE_DIR}/logs/warning.log', 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    break
                response.write(f"data: {line}\n\n")  # Send log data as SSE event

        return response

    @staticmethod
    def log(request):
        if request.method == "POST":
            log_file_path = f'{BASE_DIR}/error/info.log'  # Replace with your log file path
            with open(log_file_path, 'r') as file:
                log_data = file.readlines()

            if request.POST.get('start') and request.POST.get('length'):
                page = int(request.POST.get('start')) // int(request.POST.get('length')) + 1
            else:
                page = 0

            per_page = str(request.POST.get('length') if request.POST.get('length') else 20)
            paginator = Paginator(log_data, per_page)
            page_data = paginator.get_page(page)

            log_entries = [{'LogEntry': entry} for entry in page_data]
            return JsonResponse({'data': log_entries, 'recordsTotal': len(log_data), 'recordsFiltered': paginator.count})

        return render(request, 'backend/system/logs/view.html')
