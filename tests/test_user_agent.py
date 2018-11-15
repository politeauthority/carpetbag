"""Test UserAgent
Run by using "pytest ." in the project root.

"""
from carpetbag import user_agent


class TestUserAgent(object):

    def test_get_random_ua(self):
        """
        Tests the random user agent functionality of the user_agent module.

        """
        user_agent_1 = user_agent.get_random_ua()
        user_agent_2 = user_agent.get_random_ua(except_user_agent=user_agent_1)

        assert isinstance(user_agent_1, str)
        assert user_agent_1 in user_agent.get_flattened_uas()
        assert user_agent_1 != user_agent_2

    def test_get_flattened_uas(self):
        """
        Tests the get flattened_uas method to make sure it returns a list with one of our known user agent strings
        in it.

        """
        uas = user_agent.get_flattened_uas()

        assert isinstance(uas, list)
        assert "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0" in uas

# EndFile: carpetbag/tests/test_user_agent.py
