# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps

from django.core.urlresolvers import reverse
from django.http import Http404

from django_tinsel.utils import decorate as do

from apps.home.training.routes import make_flatpage_route
from apps.home.training.decorators import mark_user, require_visitability
from apps.users.models import TrainingResult

_PURE_URL_NAME_TEMPLATE = '%s_pure'
_MARK_PROGRESS_URL_NAME_TEMPLATE = '%s_mark_progress'
_TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE = 'training_finished_%s'


class AbstractTrainingNode(object):
    def pure_kwargs(self):
        return {'name': _PURE_URL_NAME_TEMPLATE % self.name,
                'view': require_visitability(self)(self.view)}

    def mark_kwargs(self):
        """
        This dictionary, when given as a **kwarg argument to a
        `url()` function call, produce an endpoint that will mark progress
        for the associated boolean when visited.
        """
        raise NotImplementedError()

    def is_complete(self):
        raise NotImplementedError()

    def is_visitable(self, user):
        raise NotImplementedError()


class TrainingGateway(AbstractTrainingNode):
    """
    A TrainingGateway is a doubly-linked list of step objects.

    TrainingGateway is step-like, allowing the list of steps to
    function as a cycle, so that no step need function as a terminal
    node. This is important because individual steps need to point to
    a next and/or previous step in order to build a 'mark_progress'
    url, a URL to another page that indicates the current page has
    been completed.

    A TrainingGateway is the main interface by which the rest of the
    application should talk to the training workflow. Where possible,
    TrainingStep objects should not be referenced directly.
    """
    def __init__(self, name, view, steps, on_user_completion=None):
        # read the step array and link the end nodes into
        # a cycle through the training gateway
        first_step, last_step = steps[0], steps[-1]
        self.previous_step = last_step
        self.next_step = first_step

        # read the step array and link non-end nodes together
        # bi-directionally
        first_step.previous_step = self
        for i, step in enumerate(steps):
            if i > 0:
                step.previous_step = steps[i - 1]
            if i < len(steps) - 1:
                step.next_step = steps[i + 1]
        for i in range(1, len(steps) - 1):
            steps[i].previous_step = steps[i-1]
            steps[i].next_step = steps[i+1]
        last_step.next_step = self

        last_step.extra_user_actions = on_user_completion

        self.name = name
        self.view = view
        self.steps = steps

    def get_step(self, name):
        for step in self.steps:
            if step.name == name:
                return step
        raise ValueError()

    def is_complete(self, user):
        return all([step.is_complete(user) for step in self.steps])

    def is_started(self, user):
        return (user.is_authenticated() and
                any([step.is_complete(user) for step in self.steps]))

    def is_visitable(self, user):
        return True

    def get_context(self, user):
        last_was_complete = True
        next_step = None

        training_steps = []
        for step in self.steps:
            is_complete = step.is_complete(user)
            if next_step is None and last_was_complete and not is_complete:
                next_step = step
                is_next = True
            else:
                is_next = False
            training_steps.append({'step': step,
                                   'is_visitable': is_complete or is_next,
                                   'is_complete': is_complete,
                                   'is_next': is_next})
            last_was_complete = is_complete

        return {'is_started': self.is_started(user),
                'training_steps': training_steps}

    def mark_kwargs(self):
        raise ValueError('Gateways do not have a progress boolean')


class AbstractTrainingStep(AbstractTrainingNode):

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.next_step = None
        self.previous_step = None
        self.extra_user_actions = None

    def pure_url(self):
        return reverse(_PURE_URL_NAME_TEMPLATE % self.name)

    def mark_progress_url(self):
        return reverse(_MARK_PROGRESS_URL_NAME_TEMPLATE % self.name)

    def mark_kwargs(self):
        name = _MARK_PROGRESS_URL_NAME_TEMPLATE % self.name
        view = do(
            require_visitability(self),
            mark_user(_TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE % self.name,
                      self.extra_user_actions),
            require_visitability(self.next_step),
            self.next_step.view)
        return {'name': name, 'view': view}

    def is_visitable(self, user):
        if self.is_complete(user):
            return True
        step = self.previous_step
        while isinstance(step, AbstractTrainingStep):
            if not step.is_complete(user):
                return False
            step = step.previous_step
        return True

    def is_complete(self, user):
        return getattr(user,
                       _TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE % self.name,
                       False)

    def __str__(self):
        return self.name


class FlatPageTrainingStep(AbstractTrainingStep):
    flatpage_template_name = 'flatpages/training.html'

    def __init__(self, *args, **kwargs):
        super(FlatPageTrainingStep, self).__init__(*args, **kwargs)
        self.view = make_flatpage_route(self.name)


class ViewTrainingStep(AbstractTrainingStep):
    def __init__(self, view, *args, **kwargs):
        super(ViewTrainingStep, self).__init__(*args, **kwargs)
        self.view = view


class QuizTrainingStep(ViewTrainingStep):
    def __init__(self, quiz, view, *args, **kwargs):
        super(QuizTrainingStep, self).__init__(view, *args, **kwargs)
        self.quiz = quiz

    def require_training_result(self, view_fn):
        @wraps(view_fn)
        def wrapper(request, *args, **kwargs):
            training_results = (TrainingResult.objects
                                .filter(user=request.user.id,
                                        module_name=self.quiz.slug,
                                        score__gte=self.quiz.passing_score))
            if not training_results.exists():
                raise Http404()
            else:
                return view_fn(request, *args, **kwargs)
        return wrapper

    def mark_kwargs(self):
        ctx = super(QuizTrainingStep, self).mark_kwargs()
        new_view = self.require_training_result(ctx['view'])
        ctx['view'] = new_view
        return ctx


class Quiz(object):
    """
    slug - string; an internally available reference to the slug used to
           access this quiz from the outside world via the global `quizzes`
           dict.
    title - string
    questions - iterable<Question>
    passing_score - int; Number of correct answers needed to pass the quiz
    """
    def __init__(self, slug, title, help_text, questions, passing_score):
        assert len(questions) > 0
        assert passing_score <= len(questions)
        self.slug = unicode(slug)
        self.title = unicode(title)
        self.help_text = unicode(help_text)
        self.questions = list(questions)
        self.passing_score = int(passing_score)

    @classmethod
    def extract_answers(cls, post_fields):
        """
        Return dict of {question_index => answer_indexes, ...} from post fields
        post_fields - QueryDict; Probably from request.POST
        """
        result = []
        for field_name, values in post_fields.iterlists():
            # Parse field name format like "question.1", "question.2", etc.
            parts = field_name.split('.')
            if len(parts) == 2 and parts[0] == 'question':
                try:
                    answers = map(int, values)
                    question_index = int(parts[1])
                    result.append((question_index, answers))
                except ValueError:
                    pass
        return dict(result)

    def correct_answers(self, answers):
        """Return indexes of correctly answered questions"""
        for i, question in enumerate(self.questions):
            answer = answers.get(i, None)
            if question.is_correct(answer):
                yield i

    def score(self, answers):
        """
        Return number of correctly answered questions.
        answers - dict of {question_index => answer_indexes, ...}
        """
        return len(list(self.correct_answers(answers)))


class Question(object):
    """
    Represents a question with multiple correct answers.
    text - string
    choices - iterable<string>
    answer - SingleAnswer or MultipleAnswer object
    """
    def __init__(self, text, choices, answer,
                 correct_markup="", incorrect_markup=""):
        assert len(choices) > 0
        for ans in answer.answers:
            assert ans >= 0
            assert ans < len(choices)
        self.text = unicode(text)
        self.correct_markup = correct_markup
        self.incorrect_markup = incorrect_markup
        self.choices = list(choices)
        self.answer = answer

    def is_correct(self, candidate):
        return candidate and set(candidate) == set(self.answer.answers)

    def allow_multiple_selections(self):
        return type(self.answer) is MultipleAnswer


class MultipleAnswer(object):
    """
    answer - iterable<int>; Indexes of correct answers in `choices` iterable
    """
    def __init__(self, *answers):
        self.answers = list(answers)


class SingleAnswer(MultipleAnswer):
    """
    answer - int; Index of correct answer in `choices` iterable
    """
    def __init__(self, answer):
        super(SingleAnswer, self).__init__(answer)
