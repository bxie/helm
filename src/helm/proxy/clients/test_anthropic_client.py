import os
import tempfile
from typing import List

from helm.common.cache import SqliteCacheConfig
from helm.common.tokenization_request import (
    DecodeRequest,
    DecodeRequestResult,
    TokenizationRequest,
    TokenizationRequestResult,
)
from .anthropic_client import AnthropicClient


class TestAnthropicCleint:
    TEST_PROMPT: str = "I am a computer scientist."
    TEST_ENCODED: List[int] = [45, 1413, 269, 6797, 22228, 18]
    TEST_TOKENS: List[str] = ["I", "Ġam", "Ġa", "Ġcomputer", "Ġscientist", "."]

    def setup_method(self, method):
        cache_file = tempfile.NamedTemporaryFile(delete=False)
        self.cache_path: str = cache_file.name
        self.client = AnthropicClient(SqliteCacheConfig(self.cache_path))

    def teardown_method(self, method):
        os.remove(self.cache_path)

    def test_tokenize(self):
        request = TokenizationRequest(text=self.TEST_PROMPT)
        result: TokenizationRequestResult = self.client.tokenize(request)
        assert not result.cached, "First time making the tokenize request. Result should not be cached"
        result: TokenizationRequestResult = self.client.tokenize(request)
        assert result.cached, "Result should be cached"
        assert result.raw_tokens == self.TEST_TOKENS

    def test_encode(self):
        request = TokenizationRequest(text=self.TEST_PROMPT, encode=True, truncation=True, max_length=1)
        result: TokenizationRequestResult = self.client.tokenize(request)
        assert not result.cached, "First time making the tokenize request. Result should not be cached"
        result: TokenizationRequestResult = self.client.tokenize(request)
        assert result.cached, "Result should be cached"
        assert result.raw_tokens == [self.TEST_ENCODED[0]]

        request = TokenizationRequest(text=self.TEST_PROMPT, encode=True, truncation=True, max_length=1024)
        result = self.client.tokenize(request)
        assert not result.cached, "First time making this particular request. Result should not be cached"
        assert result.raw_tokens == self.TEST_ENCODED

    def test_decode(self):
        request = DecodeRequest(tokens=self.TEST_ENCODED)
        result: DecodeRequestResult = self.client.decode(request)
        assert not result.cached, "First time making the decode request. Result should not be cached"
        result: DecodeRequestResult = self.client.decode(request)
        assert result.cached, "Result should be cached"
        assert result.text == self.TEST_PROMPT

        # Checks that decode also works with a list of strings
        request_str = DecodeRequest(tokens=self.TEST_TOKENS)
        result_str: DecodeRequestResult = self.client.decode(request_str)
        assert not result_str.cached, "First time making the decode request str. Result should not be cached"
        result_str: DecodeRequestResult = self.client.decode(request_str)
        assert result_str.cached, "Result should be cached"
        assert result_str.text == self.TEST_PROMPT
