from django.contrib import admin

from unloads.models import UnloadScheduler
from django.contrib.admin.options import (
    unquote,
    csrf_protect_m,
    HttpResponseRedirect,
)

from unloads.models import TaskStatus


class UnloadAdmin(admin.ModelAdmin):
    list_display = [
        "pk_id",
        "title",
        "service",
        "time_interval",
        "status",
        "created_at",
    ]
    list_display_links = ["pk_id", "service"]
    actions = ["delete_model"]

    def delete_model(self, request, unload_list) -> None:
        for unload in unload_list:
            unload.terminate()
            unload.delete()
        print("Deleted unload")

    change_form_template = 'unloads/admin_change_unload_form.html'


    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST' and '_setup_task' in request.POST:
            obj = self.get_object(request, unquote(object_id))
            if obj.task:
                obj.task.enabled = obj.status == TaskStatus.active
                obj.task.interval = obj.interval_schedule
                obj.task.save()
            else:
                obj.setup_task()

            return HttpResponseRedirect(request.get_full_path())

        return admin.ModelAdmin.changeform_view(
            self, request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )



admin.site.register(UnloadScheduler, UnloadAdmin)
