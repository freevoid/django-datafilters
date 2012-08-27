from django.test import TestCase


class FilterViewTestCase(TestCase):

    fixtures = ['polls/initial_data.json']

    def _test_common(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        polls = response.context_data['polls']
        self.assertEqual(len(polls), 3)

        response = self.client.get(url + '?has_exact_votes=100500')
        polls = response.context_data['polls']
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0].id, 3)

    def _test_bulk(self, url):
        response = self.client.get(url +
            '?has_exact_votes=100500&has_choice_with_votes=true&pub_date=all&has_major_choice=true&question_contains=framework&choice_contains=Flask')
        self.assertEqual(response.status_code, 200)
        polls = response.context_data['polls']
        self.assertEqual(len(polls), 0)

        response = self.client.get(url +
            '?has_exact_votes=100500&has_choice_with_votes=true&pub_date=all&has_major_choice=true&question_contains=framework&choice_contains=Django')
        self.assertEqual(response.status_code, 200)
        polls = response.context_data['polls']
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0].id, 3)

    def _test_chaining(self, url):
        response = self.client.get(url +
            '?has_exact_votes=100500&has_choice_with_votes=true&pub_date=all&has_major_choice=true&question_contains=framework&choice_contains=Flask')
        self.assertEqual(response.status_code, 200)
        polls = response.context_data['polls']
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0].id, 3)

    def test_decorated(self):
        self._test_common('/polls/decorated/')
        self._test_bulk('/polls/decorated/')

    def test_mixin(self):
        self._test_common('/polls/classbased/')
        self._test_bulk('/polls/classbased/')

    def test_mixin_chaining(self):
        self._test_common('/polls/classbased_chaining/')
        self._test_chaining('/polls/classbased_chaining/')
