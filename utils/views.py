from django.conf import settings
from django.forms import BooleanField
import requests
from typing import Any
from django.views.generic import TemplateView, ListView
from django.utils import timezone
from django.utils.dates import MONTHS
from django.db.models import Count, Q
from academic_calendar.models import AcademicCalendar
from blog.models import Post
from extracurriculars.models import Extracurricular
from galleries.models import Gallery
from laporan.models import Report
from olympiads.models import OlympiadReport
from prestasi.models import Prestasi, ProgramPrestasi
from raker.models import LaporanPertanggungJawaban, ProgramKerja
from users.models import Teacher
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse


class SMAITHomeWiew(ListView):
    model = Prestasi
    queryset = Prestasi.objects.order_by("-created_at")[:18]
    template_name = "home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["galleries"] = Gallery.objects.all()
        context["extracurriculars"] = Extracurricular.objects.filter(status="Aktif")
        context["teachers"] = Teacher.objects.exclude(id__in=["31", "112", "110", "35", "113", "111"]).filter(status="Aktif", photo__isnull=False, gender="L")
        context["news"] = Post.objects.all()[:20]
        context["academic_calendars"] = AcademicCalendar.objects.filter(Q(event_date__gte=timezone.now().date()) |
                                                                        Q(event_end_date__gte=timezone.now().date())).order_by("event_date")[:6]
        return context

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


def get_filtered_monthly_report(data: Report):
    
    filtered_reports_this_academic_year = []
    temp_list = []
    month_count = 7
    year_count = 2024
    for item in data:
        if item['report_date__month'] == month_count and item['report_date__year'] == year_count:
            item.update({'date_display': f"{MONTHS.get(item['report_date__month'])} {item['report_date__year']}"})
            temp_list.append(item)
        else:
            filtered_reports_this_academic_year.append(temp_list)
            temp_list = []
            month_count = item['report_date__month']
            year_count = item['report_date__year']
            item.update({'date_display': f"{MONTHS.get(item['report_date__month'])} {item['report_date__year']}"})
            temp_list.append(item)
    filtered_reports_this_academic_year.append(temp_list)
    return filtered_reports_this_academic_year


class LPJPMBPView(TemplateView):
    template_name = 'lpj.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        lpj = list(LaporanPertanggungJawaban.objects.filter(tahun_ajaran=settings.TAHUN_AJARAN_LALU))
        lpj_terlaksana = [item for item in lpj if item.status == "Terlaksana"]
        lpj_tidak_terlaksana = [item for item in lpj if item.status == "Tidak Terlaksana"]
        achievements_this_academic_year = Prestasi.objects.filter(created_at__gte=settings.TANGGAL_TAHUN_AJARAN, created_at__lte=settings.TANGGAL_TAHUN_AJARAN_END)
        achievements_prev_academic_year = Prestasi.objects.filter(created_at__gte=settings.TANGGAL_TAHUN_AJARAN_LALU, created_at__lte=settings.TANGGAL_TAHUN_AJARAN)
        
        filtered_category_achievements = [
                                            [item for item in achievements_this_academic_year if item.level.lower() == "kabupaten" or item.level.lower() == "tingkat kabupaten"],
                                            [item for item in achievements_this_academic_year if item.level.lower() == "provinsi jawa barat" or item.level.lower() == "jabar dan dki jakarta"],
                                            [item for item in achievements_this_academic_year if item.level.lower() == "nasional"],
                                            [item for item in achievements_this_academic_year if item.level.lower() == "internasional"],
                                          ]
        filtered_predicate_achievements = [
                                            [item for item in achievements_this_academic_year if item.predicate.lower() == "juara 1" or item.predicate.lower() == "medali emas"],
                                            [item for item in achievements_this_academic_year if item.predicate.lower() == "juara 2" or item.predicate.lower() == "medali perak"],
                                            [item for item in achievements_this_academic_year if item.predicate.lower() == "juara 3" or item.predicate.lower() == "medali perunggu"],
                                            [item for item in achievements_this_academic_year if item.predicate.lower() in ["juara 4", "juara 5", "runner up", "pelantikan kenaikan tingkat", "juara dan lolos ke nasional"]],
                                          ]
        olympiad_reports_this_academic_year = OlympiadReport.objects.filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                                    .values('field_name__field_name', 'report_date__month', 'report_date__year')\
                                                                    .annotate(count=Count('field_name'))\
                                                                    .order_by('report_date__year', 'report_date__month')\
                                                                    .distinct()
        
        olympiad_reports_recap_now = OlympiadReport.objects.filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                                    .values('field_name__field_name')\
                                                                    .annotate(count=Count('field_name'))\
                                                                    .order_by()\
                                                                    .distinct()
        olympiad_reports_recap_prev = OlympiadReport.objects.filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN_LALU, report_date__lte=settings.TANGGAL_TAHUN_AJARAN)\
                                                                    .values('field_name__field_name')\
                                                                    .annotate(count=Count('field_name'))\
                                                                    .order_by()\
                                                                    .distinct()
        
        olympiad_reports = OlympiadReport.objects.filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                                    .values('report_date')
        
        olympiad_reports_this_academic_year_by_month = OlympiadReport.objects.filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                                    .values('report_date__month', 'report_date__year')\
                                                                    .annotate(count=Count('field_name'))\
                                                                    .order_by('report_date__year', 'report_date__month')\
                                                                    .distinct()
                                                                    
        reports_ekskul_this_academic_year = Report.objects.select_related('extracurricular', 'teacher')\
                                                            .filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                            .values('extracurricular__short_name', 'report_date__month', 'report_date__year')\
                                                            .annotate(count=Count('extracurricular'))\
                                                            .order_by('report_date__year', 'report_date__month')\
                                                            .distinct()
        
        reports_ekskul_recap = Report.objects.select_related('extracurricular', 'teacher')\
                                                            .filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                            .values('extracurricular__short_name')\
                                                            .annotate(count=Count('extracurricular'))\
                                                            .order_by()\
                                                            .distinct()
        
        reports_this_academic_year_by_month = Report.objects.select_related('extracurricular', 'teacher')\
                                                            .filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                            .values('report_date__month', 'report_date__year')\
                                                            .annotate(count=Count('extracurricular'))\
                                                            .order_by('report_date__year', 'report_date__month')\
                                                            .distinct()
        reports_this_academic_year = Report.objects.select_related('extracurricular', 'teacher')\
                                                            .filter(report_date__gte=settings.TANGGAL_TAHUN_AJARAN, report_date__lte=settings.TANGGAL_TAHUN_AJARAN_END)\
                                                            .values('report_date')
        
        monthly_extracurricular_reports = get_filtered_monthly_report(reports_ekskul_this_academic_year)
        monthly_olympiad_reports = get_filtered_monthly_report(olympiad_reports_this_academic_year)
        extracurriculars_and_study_groups = list(Extracurricular.objects.prefetch_related("teacher", "members").filter(status="Aktif"))
        extracurriculars = [item for item in extracurriculars_and_study_groups if item.type == "Ekskul"]
        study_clubs = [item for item in extracurriculars_and_study_groups if item.type == "SC"]
        active_extracurricular_reports = Report.objects.select_related('extracurricular', 'teacher').values_list('extracurricular', flat=True).distinct()
        active_extracurricular = [item for item in extracurriculars_and_study_groups if item.id in active_extracurricular_reports]
        inactive_extracurricular = [item for item in extracurriculars_and_study_groups if item.id not in active_extracurricular_reports]
        context = super().get_context_data(**kwargs)
        context.update({"extracurriculars_and_study_groups" : extracurriculars_and_study_groups})
        context.update({"extracurriculars" : extracurriculars})
        context.update({"study_clubs" : study_clubs})
        context["active_extracurricular"] = active_extracurricular
        context["inactive_extracurricular"] = inactive_extracurricular
        context["monthly_extracurricular_reports"] = monthly_extracurricular_reports
        context["monthly_olympiad_reports"] = monthly_olympiad_reports
        context["reports_this_academic_year_by_month"] = reports_this_academic_year_by_month
        context["olympiad_reports_this_academic_year_by_month"] = olympiad_reports_this_academic_year_by_month
        context["reports_this_academic_year"] = len(reports_this_academic_year)
        context["olympiad_reports"] = len(olympiad_reports)
        context["achievements_this_academic_year"] = achievements_this_academic_year.count()
        context["achievements_prev_academic_year"] = achievements_prev_academic_year.count()
        context["filtered_category_achievements"] = filtered_category_achievements
        context["filtered_predicate_achievements"] = filtered_predicate_achievements
        context["lpj"] = lpj
        context["lpj_terlaksana"] = lpj_terlaksana
        context["lpj_tidak_terlaksana"] = lpj_tidak_terlaksana
        context["reports_ekskul_recap"] = reports_ekskul_recap
        context["olympiad_reports_recap_now"] = olympiad_reports_recap_now
        context["olympiad_reports_recap_prev"] = olympiad_reports_recap_prev
        context["tahun_ajaran"] = settings.TAHUN_AJARAN
        context["tahun_ajaran_lalu"] = settings.TAHUN_AJARAN_LALU
        
        return context



class ProkerPMBPView(TemplateView):
    template_name = 'proker.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        proker = list(ProgramKerja.objects.filter(tahun_ajaran=settings.TAHUN_AJARAN).order_by("created_at"))
        program_prestasi = list(ProgramPrestasi.objects.filter(tanggal__gte=settings.TANGGAL_TAHUN_AJARAN, tanggal__lte=settings.TANGGAL_TAHUN_AJARAN_END))
        extracurriculars_and_study_groups = list(Extracurricular.objects.prefetch_related("teacher", "members")\
                                                .filter(status="Aktif")\
                                                .order_by("category", "name"))

        extracurriculars = [item for item in extracurriculars_and_study_groups if item.type == "Ekskul"]
        study_clubs = [item for item in extracurriculars_and_study_groups if item.type == "SC"]
        context = super().get_context_data(**kwargs)
        context.update({"extracurriculars_and_study_groups" : extracurriculars_and_study_groups})
        context.update({"extracurriculars" : extracurriculars})
        context.update({"study_clubs" : study_clubs})
        context.update({"program_prestasi" : program_prestasi})
        context["proker"] = proker
        context["proker"] = proker
        context["tahun_ajaran"] = settings.TAHUN_AJARAN
        context["tahun_ajaran_lalu"] = settings.TAHUN_AJARAN_LALU
        
        return context
    



class LatestPostsFeed(Feed):
    title = "My Blog Updates"
    link = "/rss/"
    description = "Latest posts from my blog"

    def items(self):
        return Post.objects.filter(status="published").order_by("-created_at")[:10]

    def item_title(self, item):
        return item.title

    # def item_description(self, item):
    #     return item.content  # or item.excerpt if you have one
    def item_description(self, item):
        # Include the image + excerpt
        img_url = settings.SITE_URL + item.featured_image.url if item.featured_image else ""
        return f'<p><img src="{img_url}" alt="{item.title}" /></p>{item.content}'

    def item_link(self, item):
        # Make sure your Post model has a get_absolute_url()
        return reverse("post-detail", args=[item.slug])
    
    def item_enclosures(self, item):
        if item.featured_image:
            return [settings.SITE_URL + item.featured_image.url]
        return []


class ImageAtom1Feed(Atom1Feed):
    """
    Custom Atom feed with media:content support for images
    """
    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)

        # Add <link rel="enclosure" ...> for the featured image
        if item.get("image_url"):
            handler.addQuickElement("link", "",
                {"rel": "enclosure", "href": item["image_url"], "type": "image/jpeg"}
            )

            # Or alternatively add <media:content>
            handler.startElement("media:content", {
                "url": item["image_url"],
                "medium": "image",
            })
            handler.endElement("media:content")


class LatestPostsAtomFeed(Feed):
    feed_type = ImageAtom1Feed
    title = "My Blog Updates (Atom)"
    link = "/atom/"
    subtitle = "Latest posts from my blog"

    def items(self):
        return Post.objects.filter(status="published").order_by("-created_at")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        img_url = settings.SITE_URL + item.featured_image.url if item.featured_image else ""
        return f'<p><img src="{img_url}" alt="{item.title}" /></p>{item.content}'

    def item_link(self, item):
        return reverse("post-detail", args=[item.slug])

    # Atom extra fields
    def item_author_name(self, item):
        return getattr(item.author, "teacher_name", "Unknown Author")

    def item_author_email(self, item):
        return getattr(item.author, "email", None)

    def item_pubdate(self, item):
        return item.created_at

    def item_updateddate(self, item):
        return getattr(item, "updated_at", item.created_at)

    def item_extra_kwargs(self, item):
        """Pass image URL down to custom feed generator"""
        if item.featured_image:
            return {"image_url": settings.SITE_URL + item.featured_image.url}
        return {}


# class LPJPMBPView(TemplateView):
#     template_name = 'lpj.html'

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super().get_context_data(**kwargs)

#         # Common date ranges
#         current_year_start = settings.TANGGAL_TAHUN_AJARAN
#         current_year_end = settings.TANGGAL_TAHUN_AJARAN_END
#         prev_year_start = settings.TANGGAL_TAHUN_AJARAN_LALU

#         # Fetch LPJ data
#         lpj_queryset = LaporanPertanggungJawaban.objects.filter(tahun_ajaran=settings.TAHUN_AJARAN)
#         lpj = list(lpj_queryset)
#         lpj_status = {item.status: [] for item in lpj}
#         for item in lpj:
#             lpj_status[item.status].append(item)

#         # Fetch achievements
#         achievements = Prestasi.objects.filter(
#             created_at__range=(prev_year_start, current_year_end)
#         ).annotate(
#             is_current=Case(
#                 When(created_at__gte=current_year_start, then=Value(True)),
#                 default=Value(False),
#             )
#         )
#         achievements_this_year = achievements.filter(is_current=True)
#         achievements_last_year = achievements.filter(is_current=False)

#         # Categorize achievements
#         levels = {
#             "kabupaten": ["kabupaten", "tingkat kabupaten"],
#             "provinsi": ["provinsi jawa barat", "jabar dan dki jakarta"],
#             "nasional": ["nasional"],
#             "internasional": ["internasional"],
#         }
#         predicates = {
#             "juara_1": ["juara 1", "medali emas"],
#             "juara_2": ["juara 2", "medali perak"],
#             "juara_3": ["juara 3", "medali perunggu"],
#             "other": ["juara 4", "juara 5", "runner up", "pelantikan kenaikan tingkat", "juara dan lolos ke nasional"],
#         }
#         filtered_category_achievements = {
#             key: achievements_this_year.filter(level__in=vals)
#             for key, vals in levels.items()
#         }
#         filtered_predicate_achievements = {
#             key: achievements_this_year.filter(predicate__in=vals)
#             for key, vals in predicates.items()
#         }

#         # Fetch Olympiad and Report Data
#         olympiad_reports = OlympiadReport.objects.filter(report_date__range=(current_year_start, current_year_end))
#         reports = Report.objects.filter(report_date__range=(current_year_start, current_year_end))

#         # Grouping and aggregating reports
#         olympiad_by_month = olympiad_reports.values('report_date__month', 'report_date__year')\
#             .annotate(count=Count('id')).order_by('report_date__year', 'report_date__month')
#         reports_by_month = reports.values('report_date__month', 'report_date__year')\
#             .annotate(count=Count('id')).order_by('report_date__year', 'report_date__month')

#         # Extracurriculars and Study Groups
#         extracurriculars_and_study_groups = Extracurricular.objects.prefetch_related("teacher", "members").all()
#         extracurriculars = extracurriculars_and_study_groups.filter(type="Ekskul")
#         study_clubs = extracurriculars_and_study_groups.filter(type="SC")

#         # Active/Inactive extracurriculars
#         active_extracurricular_ids = reports.values_list('extracurricular_id', flat=True).distinct()
#         active_extracurricular = extracurriculars_and_study_groups.filter(id__in=active_extracurricular_ids)
#         inactive_extracurricular = extracurriculars_and_study_groups.exclude(id__in=active_extracurricular_ids)

#         # Update context
#         context.update({
#             "lpj": lpj,
#             "lpj_terlaksana": lpj_status.get("Terlaksana", []),
#             "lpj_tidak_terlaksana": lpj_status.get("Tidak Terlaksana", []),
#             "achievements_this_academic_year": achievements_this_year.count(),
#             "achievements_prev_academic_year": achievements_last_year.count(),
#             "filtered_category_achievements": filtered_category_achievements,
#             "filtered_predicate_achievements": filtered_predicate_achievements,
#             "monthly_extracurricular_reports": reports_by_month,
#             "monthly_olympiad_reports": olympiad_by_month,
#             "extracurriculars_and_study_groups": extracurriculars_and_study_groups,
#             "extracurriculars": extracurriculars,
#             "study_clubs": study_clubs,
#             "active_extracurricular": active_extracurricular,
#             "inactive_extracurricular": inactive_extracurricular,
#         })

#         return context
