import json
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import WorkoutSession, Exercise, SetLog, MUSCLE_GROUPS, DAYS_OF_WEEK


# ─── Auth Views ───────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'tracker/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if not username or not password1:
            messages.error(request, 'Username and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, f'Welcome to IronLog, {username}!')
            return redirect('dashboard')
    return render(request, 'tracker/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            email = request.POST.get('email', '').strip()
            request.user.email = email
            request.user.save()
            messages.success(request, 'Profile updated.')
        elif action == 'change_password':
            old_pw = request.POST.get('old_password', '')
            new_pw1 = request.POST.get('new_password1', '')
            new_pw2 = request.POST.get('new_password2', '')
            if not request.user.check_password(old_pw):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw1 != new_pw2:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw1) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_pw1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
        return redirect('profile')

    total_sessions = WorkoutSession.objects.filter(user=request.user).count()
    total_exercises = Exercise.objects.filter(session__user=request.user).count()
    total_sets = SetLog.objects.filter(exercise__session__user=request.user).count()
    return render(request, 'tracker/profile.html', {
        'total_sessions': total_sessions,
        'total_exercises': total_exercises,
        'total_sets': total_sets,
    })


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    sessions = WorkoutSession.objects.filter(user=request.user).prefetch_related('exercises__sets')
    recent = sessions[:5]
    total_sessions = sessions.count()
    total_exercises = Exercise.objects.filter(session__user=request.user).count()
    muscle_stats = {}
    for s in sessions:
        for m in s.muscle_groups_list():
            muscle_stats[m] = muscle_stats.get(m, 0) + 1
    return render(request, 'tracker/dashboard.html', {
        'recent_sessions': recent,
        'total_sessions': total_sessions,
        'total_exercises': total_exercises,
        'muscle_stats': sorted(muscle_stats.items(), key=lambda x: x[1], reverse=True)[:6],
        'today': date.today().strftime('%Y-%m-%d'),
        'today_day': date.today().strftime('%A'),
    })


# ─── Session CRUD ─────────────────────────────────────────────────────────────

@login_required
def session_list(request):
    sessions = WorkoutSession.objects.filter(user=request.user).prefetch_related('exercises__sets')
    return render(request, 'tracker/session_list.html', {'sessions': sessions})


@login_required
def session_detail(request, pk):
    session = get_object_or_404(
        WorkoutSession.objects.prefetch_related('exercises__sets'),
        pk=pk, user=request.user
    )
    return render(request, 'tracker/session_detail.html', {'session': session})


@login_required
def session_new(request):
    if request.method == 'POST':
        muscles = ','.join(request.POST.getlist('muscle_groups'))
        session = WorkoutSession.objects.create(
            user=request.user,
            date=request.POST['date'],
            day=request.POST['day'],
            muscle_groups=muscles,
            notes=request.POST.get('notes', ''),
        )
        return redirect('session_detail', pk=session.pk)
    return render(request, 'tracker/session_form.html', {
        'muscle_groups': MUSCLE_GROUPS,
        'days': DAYS_OF_WEEK,
        'today': date.today().strftime('%Y-%m-%d'),
        'today_day': date.today().strftime('%A'),
    })


@login_required
def session_edit(request, pk):
    session = get_object_or_404(WorkoutSession, pk=pk, user=request.user)
    if request.method == 'POST':
        muscles = ','.join(request.POST.getlist('muscle_groups'))
        session.date = request.POST['date']
        session.day = request.POST['day']
        session.muscle_groups = muscles
        session.notes = request.POST.get('notes', '')
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


@login_required
def session_delete(request, pk):
    session = get_object_or_404(WorkoutSession, pk=pk, user=request.user)
    if request.method == 'POST':
        session.delete()
        return redirect('session_list')
    return render(request, 'tracker/session_confirm_delete.html', {'session': session})


# ─── AJAX API (all user-scoped) ───────────────────────────────────────────────

@login_required
@require_POST
def api_add_exercise(request, session_pk):
    session = get_object_or_404(WorkoutSession, pk=session_pk, user=request.user)
    data = json.loads(request.body)
    exercise = Exercise.objects.create(
        session=session, name=data['name'], order=session.exercises.count()
    )
    return JsonResponse({'id': exercise.pk, 'name': exercise.name, 'order': exercise.order})


@login_required
@require_http_methods(['DELETE'])
def api_delete_exercise(request, exercise_pk):
    exercise = get_object_or_404(Exercise, pk=exercise_pk, session__user=request.user)
    exercise.delete()
    return JsonResponse({'status': 'deleted'})


@login_required
@require_POST
def api_add_set(request, exercise_pk):
    exercise = get_object_or_404(Exercise, pk=exercise_pk, session__user=request.user)
    data = json.loads(request.body)
    s = SetLog.objects.create(
        exercise=exercise,
        set_number=exercise.sets.count() + 1,
        weight=data.get('weight') or None,
        weight_unit=data.get('weight_unit', 'kg'),
        reps=data.get('reps') or None,
        notes=data.get('notes', ''),
    )
    return JsonResponse({
        'id': s.pk, 'set_number': s.set_number,
        'weight': str(s.weight) if s.weight else '',
        'weight_unit': s.weight_unit, 'reps': s.reps or '', 'notes': s.notes,
    })


@login_required
@require_POST
def api_update_set(request, set_pk):
    s = get_object_or_404(SetLog, pk=set_pk, exercise__session__user=request.user)
    data = json.loads(request.body)
    s.weight = data.get('weight') or None
    s.weight_unit = data.get('weight_unit', 'kg')
    s.reps = data.get('reps') or None
    s.notes = data.get('notes', '')
    s.save()
    return JsonResponse({'status': 'updated'})


@login_required
@require_http_methods(['DELETE'])
def api_delete_set(request, set_pk):
    s = get_object_or_404(SetLog, pk=set_pk, exercise__session__user=request.user)
    s.delete()
    return JsonResponse({'status': 'deleted'})
