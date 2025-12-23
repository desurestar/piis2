from courses.models import Course
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView

from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    # было students/student/registration.html — такого файла нет
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('students:student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password1'])
        if user:
            login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    form_class = CourseEnrollForm
    template_name = None  # мы используем форму через POST c кнопки на странице курса
    course = None
    http_method_names = ['post']  # запретим GET, чтобы не требовать template_name

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('students:student_course_detail', args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    # было 'courses/course/list.html' — ожидал другой контекст
    template_name = 'students/course/list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    # было 'courses/course/detail.html' — не тот шаблон
    template_name = 'students/course/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        # выбор модуля: module_id в kwargs или первый модуль
        module = None
        if 'module_id' in self.kwargs:
            module = course.modules.get(id=self.kwargs['module_id'])
        else:
            modules = course.modules.all()
            module = modules[0] if modules else None
        context['module'] = module
        return context
