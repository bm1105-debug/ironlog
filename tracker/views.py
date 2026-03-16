import json
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import WorkoutSession, Exercise, SetLog, MUSCLE_GROUPS, DAYS_OF_WEEK


def dashboard(request):
    sessions = WorkoutSession.objects.prefetch_related('exercises__sets').all()
    recent = sessions[:5]
    total_sessions = sessions.count()
    total_exercises = Exercise.objects.count()
    # Stats per muscle group
    muscle_stats = {}
    for s in sessions:
        for m in s.muscle_groups_list():
            muscle_stats[m] = muscle_stats.get(m, 0) + 1

    context = {
        'recent_sessions': recent,
        'total_sessions': total_sessions,
        'total_exercises': total_exercises,
        'muscle_stats': sorted(muscle_stats.items(), key=lambda x: x[1], reverse=True)[:6],
        'today': date.today().strftime('%Y-%m-%d'),
        'today_day': date.today().strftime('%A'),
    }
    return render(request, 'tracker/dashboard.html', context)


def session_list(request):
    sessions = WorkoutSession.objects.prefetch_related('exercises__sets').all()
    return render(request, 'tracker/session_list.html', {'sessions': sessions})


def session_detail(request, pk):
    session = get_object_or_404(WorkoutSession.objects.prefetch_related('exercises__sets'), pk=pk)
    return render(request, 'tracker/session_detail.html', {
        'session': session,
        'muscle_groups': MUSCLE_GROUPS,
    })


def session_new(request):
    if request.method == 'POST':
        data = request.POST
        muscles = ','.join(data.getlist('muscle_groups'))
        session = WorkoutSession.objects.create(
            date=data['date'],
            day=data['day'],
            muscle_groups=muscles,
            notes=data.get('notes', ''),
        )
        return redirect('session_detail', pk=session.pk)
    return render(request, 'tracker/session_form.html', {
        'muscle_groups': MUSCLE_GROUPS,
        'days': DAYS_OF_WEEK,
        'today': date.today().strftime('%Y-%m-%d'),
        'today_day': date.today().strftime('%A'),
    })


def session_edit(request, pk):
    session = get_object_or_404(WorkoutSession, pk=pk)
    if request.method == 'POST':
        data = request.POST
        muscles = ','.join(data.getlist('muscle_groups'))
        session.date = data['date']
        session.day = data['day']
        session.muscle_groups = muscles
        session.notes = data.get('notes', '')
        session.save()
        return redirect('session_detail', pk=session.pk)
    return render(request, 'tracker/session_form.html', {
        'session': session,
        'muscle_groups': MUSCLE_GROUPS,
        'days': DAYS_OF_WEEK,
        'today': date.today().strftime('%Y-%m-%d'),
        'today_day': date.today().strftime('%A'),
        'selected_muscles': session.muscle_groups_list(),
    })


def session_delete(request, pk):
    session = get_object_or_404(WorkoutSession, pk=pk)
    if request.method == 'POST':
        session.delete()
        return redirect('session_list')
    return render(request, 'tracker/session_confirm_delete.html', {'session': session})


# --- AJAX API endpoints ---

@require_POST
def api_add_exercise(request, session_pk):
    session = get_object_or_404(WorkoutSession, pk=session_pk)
    data = json.loads(request.body)
    order = session.exercises.count()
    exercise = Exercise.objects.create(
        session=session,
        name=data['name'],
        order=order,
    )
    return JsonResponse({'id': exercise.pk, 'name': exercise.name, 'order': exercise.order})


@require_http_methods(['DELETE'])
def api_delete_exercise(request, exercise_pk):
    exercise = get_object_or_404(Exercise, pk=exercise_pk)
    exercise.delete()
    return JsonResponse({'status': 'deleted'})


@require_POST
def api_add_set(request, exercise_pk):
    exercise = get_object_or_404(Exercise, pk=exercise_pk)
    data = json.loads(request.body)
    set_number = exercise.sets.count() + 1
    s = SetLog.objects.create(
        exercise=exercise,
        set_number=set_number,
        weight=data.get('weight') or None,
        weight_unit=data.get('weight_unit', 'kg'),
        reps=data.get('reps') or None,
        notes=data.get('notes', ''),
    )
    return JsonResponse({
        'id': s.pk,
        'set_number': s.set_number,
        'weight': str(s.weight) if s.weight else '',
        'weight_unit': s.weight_unit,
        'reps': s.reps,
        'notes': s.notes,
    })


@require_POST
def api_update_set(request, set_pk):
    s = get_object_or_404(SetLog, pk=set_pk)
    data = json.loads(request.body)
    s.weight = data.get('weight') or None
    s.weight_unit = data.get('weight_unit', 'kg')
    s.reps = data.get('reps') or None
    s.notes = data.get('notes', '')
    s.save()
    return JsonResponse({'status': 'updated'})


@require_http_methods(['DELETE'])
def api_delete_set(request, set_pk):
    s = get_object_or_404(SetLog, pk=set_pk)
    s.delete()
    return JsonResponse({'status': 'deleted'})


def api_session_data(request, session_pk):
    session = get_object_or_404(WorkoutSession.objects.prefetch_related('exercises__sets'), pk=session_pk)
    data = {
        'id': session.pk,
        'date': str(session.date),
        'day': session.day,
        'muscle_groups': session.muscle_groups_list(),
        'notes': session.notes,
        'exercises': []
    }
    for ex in session.exercises.all():
        ex_data = {'id': ex.pk, 'name': ex.name, 'sets': []}
        for s in ex.sets.all():
            ex_data['sets'].append({
                'id': s.pk,
                'set_number': s.set_number,
                'weight': str(s.weight) if s.weight else '',
                'weight_unit': s.weight_unit,
                'reps': s.reps or '',
                'notes': s.notes,
            })
        data['exercises'].append(ex_data)
    return JsonResponse(data)
