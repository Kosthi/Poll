from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F

from .models import Question, Choice

def index(request):
    latest_questions_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'latest_questions_list': latest_questions_list,
    }
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        select_choice = question.choice_set.filter(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'You did\'t select a choice',
        })
    else:
        # select_choice.votes += 1
        # select_choice.save()
        # 避免竞争条件
        select_choice.update(votes=F('votes') + 1)
        return HttpResponseRedirect(reverse('polls:result', args=(question_id,)))

