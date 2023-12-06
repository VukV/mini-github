from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User
from apps.history.models import History, HistoryType, ChangeAction


class HistoryModelTest(TestCase):

    def test_create_history_entry(self):
        user = User.objects.create_user(username='testuser', password='testpass123')

        history_entry = History.objects.create(
            user_changed=user,
            type=HistoryType.REPOSITORY.value,
            changed_id=1,
            changed_action=ChangeAction.CREATED.value,
            changed_name='My Repository'
        )

        self.assertEqual(history_entry.user_changed, user)
        self.assertEqual(history_entry.type, HistoryType.REPOSITORY.value)
        self.assertEqual(history_entry.changed_id, 1)
        self.assertEqual(history_entry.changed_action, ChangeAction.CREATED.value)
        self.assertEqual(history_entry.changed_name, 'My Repository')

    def test_history_entry_string_representation(self):
        user = User.objects.create_user(username='testuser', password='testpass123')

        history_entry = History.objects.create(
            user_changed=user,
            type=HistoryType.PROJECT.value,
            changed_id=2,
            changed_action=ChangeAction.DELETED.value,
            changed_name='Project XYZ'
        )

        expected_str = f'{user.username} {ChangeAction.DELETED.value} {HistoryType.PROJECT.value}: Project XYZ'
        self.assertEqual(str(history_entry), expected_str)
