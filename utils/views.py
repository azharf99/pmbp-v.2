import requests
from typing import Any
from django.views.generic import TemplateView
    

class CurrationListView(TemplateView):
    template_name = "kurasi.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        page = int(self.request.GET.get("page", 1)) or 1
        per_page = self.request.GET.get("per_page", 9) or 9
        query = self.request.GET.get("query", "")
        category = self.request.GET.get("category", "")
        organizer_type = self.request.GET.get("organizer_type", "")
        start_date = self.request.GET.get("start_date", "")
        end_date = self.request.GET.get("end_date", "")
        rate_kurasi = self.request.GET.get("rate_kurasi", "")
        
        if query or category or rate_kurasi or organizer_type:
            url = f"https://simt.kemdikbud.go.id/api/v2/list-kurasi?page={page}&per_page={per_page}&competition_name={query}&category={category}&rate_kurasi={rate_kurasi}&organizer_type={organizer_type}&start_date={start_date}&end_date={end_date}"
            url_organizer = f"https://simt.kemdikbud.go.id/api/v2/list-kurasi?page={page}&per_page={per_page}&organizer={query}&category={category}&rate_kurasi={rate_kurasi}&organizer_type={organizer_type}&start_date={start_date}&end_date={end_date}"
        else:
            url = f"https://simt.kemdikbud.go.id/api/v2/list-kurasi?page={page}&per_page={per_page}"
    
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://simt.kemdikbud.go.id/"
        }

        if query:
            response1 = requests.get(url, headers=headers)
            response2 = requests.get(url_organizer, headers=headers)
            res = response1.json()
            res1 = response2.json()

            list1 = res['result']['list']
            list2 = res1['result']['list']

            length1 = len(list1)
            length2 = len(list2)

            if length1 > length2:
                for data in list2:
                    if not data in list1:
                        list1.append(data)
            else:
                for data in list1:
                    if not data in list1:
                        list2.append(data)
                res = res1
        else:
            response = requests.get(url, headers=headers)
            res = response.json()
        
        context = super().get_context_data(**kwargs)
        total_page = res['result']['pagination']['total_page']
        context.update({"object_list": res['result']['list']})
        context.update({"total_page": total_page})
        context.update({"query": query})
        context.update({"category": category})
        context.update({"rate_kurasi": str(rate_kurasi)})
        context.update({"organizer_type": organizer_type})
        if page > 1 and page < total_page :
            context.update({"prev_page": page-1})
            context.update({"next_page": page+1})
        elif page == 1:
            context.update({"next_page": page+1})
        elif page == total_page:
            context.update({"prev_page": page-1})
        
        if total_page > 1:
            context.update({"page": page})
        context.update({"per_page": str(per_page)})
        return context