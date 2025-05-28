import unittest
from unittest.mock import patch, MagicMock
from bible_search import load_verses, semantic_search_verses

class TestBibleSearch(unittest.TestCase):
    def setUp(self):
        """테스트에 필요한 초기 설정"""
        self.test_verses = [
            {'reference': '요한복음 1:35-42', 'content': '다음 날 요한이 다시 자기 제자 두 사람과 함께 서 있다가'},
            {'reference': '요한복음 1:43-51', 'content': '다음 날 예수께서 갈릴리로 나가려 하시다가 빌립을 만나 이르시되 나를 따르라 하시니'},
            {'reference': '요한복음 6:67-71', 'content': '예수께서 열두 제자에게 이르시되 너희도 가려느냐'},
            {'reference': '요한복음 13:1-17', 'content': '유월절 전에 예수께서 자기가 세상을 떠나 아버지께로 돌아가실 때가 이른 줄 아시고'},
            {'reference': '요한복음 20:24', 'content': '열두 제자 중의 하나인 디두모라 하는 도마는 예수께서 오셨을 때에 함께 있지 아니한지라'}
        ]

    @patch('bible_search.genai.GenerativeModel')
    def test_semantic_search_disciples(self, mock_model):
        """예수님의 제자 수에 대한 의미론적 검색 테스트"""
        # Mock response 설정
        mock_response = MagicMock()
        mock_response.text = """
        요한복음 6:67-71
        요한복음 20:24
        """
        mock_model.return_value.generate_content.return_value = mock_response

        # 테스트 실행
        query = "예수님의 제자는 몇 명인가요?"
        result = semantic_search_verses(self.test_verses, query)

        # 결과 검증
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        
        # 제자 수와 관련된 구절이 포함되어 있는지 확인
        references = [verse['reference'] for verse in result]
        self.assertTrue(any('6:67' in ref for ref in references))  # 열두 제자 언급
        self.assertTrue(any('20:24' in ref for ref in references))  # 열두 제자 언급

    def test_load_verses(self):
        """성경 구절 로드 테스트"""
        verses = load_verses()
        self.assertIsNotNone(verses)
        self.assertTrue(len(verses) > 0)
        self.assertTrue(all('reference' in verse for verse in verses))
        self.assertTrue(all('content' in verse for verse in verses))

if __name__ == '__main__':
    unittest.main() 