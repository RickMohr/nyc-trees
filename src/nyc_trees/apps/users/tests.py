# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import LineString
from django.http import Http404
from django.test import TestCase

from apps.core.models import User, Group
from apps.core.test_utils import make_request

from apps.survey.models import Tree, Species, Blockface, Survey

from apps.users.models import Follow, Achievement, achievements
from apps.users.views.user import user_detail, user_detail_view


class ProfileTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='pat',
            password='password',
            email='pat@rat.com',
            first_name='Pat',
            last_name='Smith',
            profile_is_public=True,
        )
        self.other_user = User.objects.create(username='other', password='a')
        self.group = Group.objects.create(
            name='The Best Group of All',
            slug='the-best-group',
            contact_email='best@group.com',
            contact_url='https://thebest.nyc',
            admin=self.other_user
        )
        Follow.objects.create(group=self.group, user=self.user)
        self.achievement = Achievement.objects.create(
            user=self.user,
            achievement_name=achievements.keys()[0]
        )

    def _update_user(self, **kwargs):
        User.objects.filter(pk=self.user.pk).update(**kwargs)

    def _render_profile(self, its_me):
        viewer = self.user if its_me else self.other_user
        request = make_request(user=viewer)
        return user_detail(request, self.user.username)

    def _assert_profile_contains(self, text, its_me=True):
        response = self._render_profile(its_me)
        self.assertContains(response, text, count=1)

    def _assert_profile_does_not_contain(self, text, its_me=True):
        response = self._render_profile(its_me)
        self.assertContains(response, text, count=0)

    def _assert_visible_to_all(self, text):
        self._assert_profile_contains(text)
        self._assert_profile_contains(text, its_me=False)

    def _assert_visible_only_to_me(self, text):
        self._assert_profile_contains(text)
        self._assert_profile_does_not_contain(text, its_me=False)

    def test_private_profile_404_if_not_me(self):
        self._update_user(profile_is_public=False)
        with self.assertRaises(Http404):
            self._render_profile(its_me=False)

    def test_username_visibility(self):
        self._assert_visible_only_to_me('Pat Smith')
        self._update_user(real_name_is_public=True)
        self._assert_visible_to_all('Pat Smith')

    def test_individual_mapper_not_shown_by_default(self):
        self._assert_profile_does_not_contain('Tree Mapper')

    def test_individual_mapper_visible_to_all(self):
        self._update_user(individual_mapper=True)
        self._assert_visible_to_all('Tree Mapper')

    def test_settings_link_visible_only_to_me(self):
        self._assert_visible_only_to_me('Settings')

    def test_groups_section_visibility(self):
        self._assert_visible_only_to_me('Groups')
        self._update_user(group_follows_are_public=True)
        self._assert_visible_to_all('Groups')

    def test_groups_section_contents(self):
        self._assert_visible_only_to_me(self.group.name)
        self._update_user(group_follows_are_public=True)
        self._assert_visible_to_all(self.group.name)

    def test_achievements_section_visibility(self):
        self._assert_visible_only_to_me('Achievements')
        self._update_user(achievements_are_public=True)
        self._assert_visible_to_all('Achievements')

    def test_achievements_section_contents(self):
        self._assert_visible_only_to_me(self.achievement.achievement_name)
        self._update_user(achievements_are_public=True)
        self._assert_visible_to_all(self.achievement.achievement_name)

    def test_contributions_section_visibility(self):
        self._assert_visible_only_to_me('Contributions')
        self._update_user(contributions_are_public=True)
        self._assert_visible_to_all('Contributions')

    def test_contributions_section_contents(self):
        blockface = Blockface.objects.create(
            geom=LineString(((0, 0), (1, 1)))
        )
        species = Species.objects.create(name='Elm')
        survey = Survey.objects.create(
            blockface=blockface,
            user=self.user
        )
        Tree.objects.create(survey=survey, species=species)
        Tree.objects.create(survey=survey, species=species)

        request = make_request(user=self.user)
        context = user_detail_view(request, self.user.username)

        self.assertIn('counts', context)
        self.assertEqual(context['counts']['block'], 1)
        self.assertEqual(context['counts']['tree'], 2)
        self.assertEqual(context['counts']['species'], 1)
