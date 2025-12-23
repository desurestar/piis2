from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import CONTENT_MODEL_MAP, ModuleFormSet
from .models import Content, Course, Module, Subject


class SubjectListView(ListView):
    model = Subject
    template_name = 'courses/subject/list.html'
    context_object_name = 'subjects'


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):

        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                total_courses=Count('courses')
            )
            cache.set('all_subjects', subjects)


        all_courses = Course.objects.annotate(
            total_modules=Count('modules')
        ).select_related('subject', 'owner')

        if subject:
            subject_obj = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject_obj.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject_obj)
                cache.set(key, courses, 600)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses, 600)

        return self.render_to_response({
            'subjects': subjects,
            'subject': subject_obj if subject else None,
            'courses': courses,
        })


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            from students.forms import CourseEnrollForm
        except Exception:
            CourseEnrollForm = None

        if CourseEnrollForm is not None:
            ctx['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return ctx


class OwnerCourseMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    context_object_name = 'courses'


class OwnerCourseEditMixin(OwnerCourseMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('courses:manage_course_list')
    template_name = 'courses/manage/course/form.html'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    pass


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('courses:manage_course_list')
    template_name = 'courses/manage/course/delete_confirm.html'


class CourseModuleUpdateView(OwnerCourseMixin, View):
    template_name = 'courses/manage/module/formset.html'

    def get(self, request, pk):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        formset = ModuleFormSet(instance=course)
        return render(request, self.template_name, {'course': course, 'formset': formset})

    def post(self, request, pk):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        formset = ModuleFormSet(instance=course, data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list')
        return render(request, self.template_name, {'course': course, 'formset': formset})


class ModuleContentListView(OwnerCourseMixin, View):
    template_name = 'courses/manage/content/list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return render(request, self.template_name, {'module': module})


class ContentCreateUpdateView(OwnerCourseMixin, View):
    template_name = 'courses/manage/content/form.html'

    def get_model_form(self, model_name):
        return CONTENT_MODEL_MAP.get(model_name)

    def get(self, request, module_id, model_name, id=None):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        model, form_class = self.get_model_form(model_name)
        if model is None:
            return redirect('courses:module_content_list', module_id=module.id)
        obj = None
        if id:
            obj = get_object_or_404(model, id=id, owner=request.user)
        form = form_class(instance=obj)
        return render(request, self.template_name, {'form': form, 'object': obj, 'model_name': model_name, 'module': module})

    def post(self, request, module_id, model_name, id=None):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        model, form_class = self.get_model_form(model_name)
        if model is None:
            return redirect('courses:module_content_list', module_id=module.id)
        obj = None
        if id:
            obj = get_object_or_404(model, id=id, owner=request.user)
        form = form_class(instance=obj, data=request.POST or None, files=request.FILES or None)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            if not id:
                Content.objects.create(module=module, item=item)
            return redirect('courses:module_content_list', module_id=module.id)
        return render(request, self.template_name, {'form': form, 'object': obj, 'model_name': model_name, 'module': module})


class ContentDeleteView(OwnerCourseMixin, View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        item = content.item
        content.delete()
        if item:
            item.delete()
        return redirect('courses:module_content_list', module_id=module.id)
