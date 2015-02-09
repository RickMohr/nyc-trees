# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse
from django_tinsel.utils import decorate as do
from apps.home.training.routes import make_flatpage_route
from apps.home.training.decorators import mark_user, require_visitability

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
    def __init__(self, name, view, steps):
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
                                   'is_complete': is_complete,
                                   'is_next': is_next})
            last_was_complete = is_complete

        return training_steps

    def mark_kwargs(self):
        raise ValueError('Gateways do not have a progress boolean')


class AbstractTrainingStep(AbstractTrainingNode):

    def __init__(self, name, description, duration):
        self.name = name
        self.description = description
        self.duration = duration
        self.next_step = None
        self.previous_step = None

    def pure_url(self):
        return reverse(_PURE_URL_NAME_TEMPLATE % self.name)

    def mark_progress_url(self):
        return reverse(_MARK_PROGRESS_URL_NAME_TEMPLATE % self.name)

    def mark_kwargs(self):
        name = _MARK_PROGRESS_URL_NAME_TEMPLATE % self.name
        view = do(
            require_visitability(self),
            mark_user(_TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE % self.name),
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


class Quiz(object):
    """
    title - string
    questions - iterable<Question>
    passing_score - int; How many correct answers are needed to pass the quiz
    """
    def __init__(self, title, questions, passing_score):
        assert len(questions) > 0
        assert passing_score <= len(questions)
        self.title = unicode(title)
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

    def score(self, answers):
        """
        How many correct answers are selected?
        answers - dict of {question_index => answer_indexes, ...}
        """
        result = 0
        for i, question in enumerate(self.questions):
            answer = answers.get(i, None)
            if question.is_correct(answer):
                result += 1
        return result


class MultiChoiceQuestion(object):
    """
    Represents a question with multiple correct answers.
    text - string
    choices - iterable<string>
    answer - iterable<int>; Indexes of the correct answers in choices iterable
    """
    def __init__(self, text, choices, answer):
        assert len(choices) > 0
        for ans in answer:
            assert ans >= 0
            assert ans < len(choices)
        self.text = unicode(text)
        self.choices = list(choices)
        self.answer = list(answer)

    def is_correct(self, candidate):
        return candidate and set(candidate) == set(self.answer)

    def is_multiple_choice(self):
        return True


class Question(MultiChoiceQuestion):
    """
    Represents a question with only one correct answer.
    text - string
    choices - iterable<string>
    answer - int; Index of the correct answer in choices iterable
    """
    def __init__(self, text, choices, answer):
        super(Question, self).__init__(text, choices, [answer])

    def is_multiple_choice(self):
        return False
