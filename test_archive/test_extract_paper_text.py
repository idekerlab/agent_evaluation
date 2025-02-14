import unittest
from unittest.mock import patch, Mock
import os
import sys
sys.path.append(os.path.abspath('..'))
from RAG.extract_paper_text import get_title  

class TestGetTitle(unittest.TestCase):
    @patch('requests.get')
    def test_get_title_no_full_text(self, mock_get):
        # Mock response for when no full text is available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<error code="idDoesNotExist">The identifier does not exist</error>'
        mock_get.return_value = mock_response


        # Test case where PMC ID does not exist
        pmc_id = 'PMC0000000'
        result = get_title(pmc_id)

        self.assertIsNone(result, "Expected None when no full text is available")

    @patch('requests.get')
    def test_get_title_with_full_text(self, mock_get):
        # Mock response for a valid PMC ID with full text
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
            <GetRecord>
                <record>
                    <metadata>
                        <article>
                            <front>
                                <article-meta>
                                    <title-group>
                                        <article-title>Sample Article Title</article-title>
                                    </title-group>
                                </article-meta>
                            </front>
                        </article>
                    </metadata>
                </record>
            </GetRecord>
        </OAI-PMH>
        '''
        mock_get.return_value = mock_response



        # Test case where PMC ID exists and has a full text
        pmc_id = 'PMC1234567'
        result = get_title(pmc_id)

        self.assertEqual(result, "Sample Article Title", "Expected the correct article title")

if __name__ == '__main__':
    unittest.main()