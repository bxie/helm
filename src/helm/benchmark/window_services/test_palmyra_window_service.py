import shutil
import tempfile
from typing import List

from .tokenizer_service import TokenizerService
from .window_service_factory import WindowServiceFactory
from .test_utils import get_tokenizer_service, TEST_PROMPT


class TestAntrhopicWindowService:
    TEST_PROMPT_LENGTH: int = 51
    TEST_TOKEN_IDS: List[int] = [
        464,
        3337,
        329,
        4992,
        319,
        5693,
        32329,
        357,
        9419,
        23264,
        8,
        318,
        281,
        987,
        40625,
        10219,
        4642,
        503,
        286,
        262,
        13863,
        5136,
        329,
        5524,
        12,
        19085,
        1068,
        35941,
        9345,
        357,
        7801,
        40,
        8,
        326,
        12031,
        284,
        787,
        7531,
        14901,
        287,
        262,
        2050,
        11,
        2478,
        11,
        290,
        14833,
        286,
        8489,
        4981,
        13,
    ]
    TEST_TOKENS: List[str] = [
        "The",
        "ĠCenter",
        "Ġfor",
        "ĠResearch",
        "Ġon",
        "ĠFoundation",
        "ĠModels",
        "Ġ(",
        "CR",
        "FM",
        ")",
        "Ġis",
        "Ġan",
        "Ġinter",
        "disciplinary",
        "Ġinitiative",
        "Ġborn",
        "Ġout",
        "Ġof",
        "Ġthe",
        "ĠStanford",
        "ĠInstitute",
        "Ġfor",
        "ĠHuman",
        "-",
        "Cent",
        "ered",
        "ĠArtificial",
        "ĠIntelligence",
        "Ġ(",
        "HA",
        "I",
        ")",
        "Ġthat",
        "Ġaims",
        "Ġto",
        "Ġmake",
        "Ġfundamental",
        "Ġadvances",
        "Ġin",
        "Ġthe",
        "Ġstudy",
        ",",
        "Ġdevelopment",
        ",",
        "Ġand",
        "Ġdeployment",
        "Ġof",
        "Ġfoundation",
        "Ġmodels",
        ".",
    ]

    def setup_method(self):
        self.path: str = tempfile.mkdtemp()
        service: TokenizerService = get_tokenizer_service(self.path)
        self.window_service = WindowServiceFactory.get_window_service("writer/palmyra-large", service)

    def teardown_method(self, method):
        shutil.rmtree(self.path)

    def test_max_request_length(self):
        assert self.window_service.max_request_length == 2048

    def test_encode(self):
        assert self.window_service.encode(TEST_PROMPT).token_values == self.TEST_TOKEN_IDS

    def test_decode(self):
        assert self.window_service.decode(self.window_service.encode(TEST_PROMPT).tokens) == TEST_PROMPT

    def test_tokenize(self):
        assert self.window_service.tokenize(TEST_PROMPT) == self.TEST_TOKENS

    def test_tokenize_and_count(self):
        assert self.window_service.get_num_tokens(TEST_PROMPT) == self.TEST_PROMPT_LENGTH

    def test_fits_within_context_window(self):
        # Should fit in the context window since we subtracted the number of tokens of the test prompt
        # from the max context window
        assert self.window_service.fits_within_context_window(
            TEST_PROMPT, self.window_service.max_request_length - self.TEST_PROMPT_LENGTH
        )
        # Should not fit in the context window because we're expecting one more extra token in the completion
        assert not self.window_service.fits_within_context_window(
            TEST_PROMPT, self.window_service.max_request_length - self.TEST_PROMPT_LENGTH + 1
        )

    def test_truncate_from_right(self):
        # Create a prompt that exceed max context length
        long_prompt: str = TEST_PROMPT * 200
        assert not self.window_service.fits_within_context_window(long_prompt)

        # Truncate and ensure it fits within the context window
        truncated_long_prompt: str = self.window_service.truncate_from_right(long_prompt)
        assert self.window_service.get_num_tokens(truncated_long_prompt) == self.window_service.max_request_length
        assert self.window_service.fits_within_context_window(truncated_long_prompt)
