from django.contrib import admin

from .models import Content, Course, Module, Subject


# Register your models here.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug']
	prepopulated_fields = {'slug': ('title',)}

class ModuleInline(admin.StackedInline):
	model = Module
	extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ['title', 'owner', 'created']
	list_filter = ['created', 'subject']
	search_fields = ['title', 'overview']
	prepopulated_fields = {'slug': ('title',)}
	inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
	list_display = ['title', 'course', 'order']

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
	list_display = ['module', 'order', 'content_type']
