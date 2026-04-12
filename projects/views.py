from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *


def project_create(request):
    projects = Project.objects.select_related('client', 'project_manager').prefetch_related('team_members').order_by('-id')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project created successfully ✅")
            return redirect('projects:project_create')
        else:
            messages.error(request, "Failed to create project ❌")
    else:
        form = ProjectForm()

    return render(request, 'projects/projects.html', {
        'form': form,
        'projects': projects
    })


def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully ✏️")
        else:
            messages.error(request, "Failed to update project ❌")

    return redirect('projects:project_create')


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('client', 'project_manager').prefetch_related('team_members', 'tasks'),
        pk=pk
    )

    task_form = ProjectTaskForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'task_form': task_form,
    })


def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f"Project '{project_name}' deleted successfully 🗑️")
    else:
        messages.warning(request, "Invalid delete request ⚠️")

    return redirect('projects:project_create')


def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ProjectTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user if request.user.is_authenticated else None
            task.save()
            messages.success(request, f"Task '{task.title}' created successfully ✅")
        else:
            messages.error(request, "Failed to create task ❌")
    else:
        messages.warning(request, "Invalid task create request ⚠️")

    return redirect('projects:project_detail', pk=project.id)


def task_update(request, task_id):
    task = get_object_or_404(ProjectTask, id=task_id)

    if request.method == 'POST':
        form = ProjectTaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, f"Task '{updated_task.title}' updated successfully ✏️")
        else:
            messages.error(request, "Failed to update task ❌")
    else:
        messages.warning(request, "Invalid task update request ⚠️")

    return redirect('projects:project_detail', pk=task.project.id)


def task_delete(request, task_id):
    task = get_object_or_404(ProjectTask, id=task_id)
    project_id = task.project.id

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f"Task '{task_title}' deleted successfully 🗑️")
    else:
        messages.warning(request, "Invalid task delete request ⚠️")

    return redirect('projects:project_detail', pk=project_id)