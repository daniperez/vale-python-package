"""Tests for transient download failures without network access or real delays."""

import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import call, patch
from urllib.error import HTTPError, URLError

from vale.main import _open_download_url


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.urlopen = self.patch("vale.main.urlopen")
        self.sleep = self.patch("vale.main.time.sleep")
        self.jitter = self.patch("vale.main.random.uniform")
        self.jitter.return_value = 3.5
        self.stderr = io.StringIO()
        self.enter_stderr = redirect_stderr(self.stderr)
        self.enter_stderr.__enter__()
        self.addCleanup(self.enter_stderr.__exit__, None, None, None)

    def patch(self, target):
        patcher = patch(target)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def http_error(self, code):
        return HTTPError(
            "https://example.com/vale", code, "test reason", {}, io.BytesIO()
        )

    def test_success_uses_timeout_without_retry(self):
        response = _open_download_url("https://example.com/vale")

        self.assertIs(response, self.urlopen.return_value)
        self.urlopen.assert_called_once_with("https://example.com/vale", timeout=60)
        self.sleep.assert_not_called()
        self.jitter.assert_not_called()
        self.assertEqual(self.stderr.getvalue(), "")

    def test_retries_all_transient_http_codes_and_closes_failed_response(self):
        for code in (408, 429, *range(500, 600)):
            with self.subTest(code=code):
                error = self.http_error(code)
                response = object()
                self.urlopen.side_effect = [error, response]

                self.assertIs(_open_download_url("url"), response)
                self.assertTrue(error.fp.closed)
                self.assertIn(f"HTTP {code}: test reason", self.stderr.getvalue())

    def test_permanent_http_errors_fail_immediately(self):
        for code in (400, 401, 403, 404, 407, 409, 428, 430, 499, 600):
            with self.subTest(code=code):
                error = self.http_error(code)
                self.addCleanup(error.close)
                self.urlopen.reset_mock()
                self.urlopen.side_effect = error

                with self.assertRaises(HTTPError) as raised:
                    _open_download_url("url")

                self.assertIs(raised.exception, error)
                self.urlopen.assert_called_once_with("url", timeout=60)
                self.sleep.assert_not_called()
                self.jitter.assert_not_called()
                self.assertEqual(self.stderr.getvalue(), "")

    def test_url_error_and_timeout_retry_with_reason(self):
        for error in (URLError("connection reset"), TimeoutError("timed out")):
            with self.subTest(error=error):
                response = object()
                self.urlopen.side_effect = [error, response]

                self.assertIs(_open_download_url("url"), response)
                self.assertIn(str(error), self.stderr.getvalue())

    def test_five_attempts_with_exponential_backoff_and_jitter(self):
        error = URLError("connection reset")
        self.urlopen.side_effect = [error] * 4 + [object()]

        response = _open_download_url("url")

        self.assertIsNotNone(response)
        self.assertEqual(self.urlopen.call_args_list, [call("url", timeout=60)] * 5)
        self.assertEqual(
            self.sleep.call_args_list, [call(n) for n in (5.5, 7.5, 11.5, 19.5)]
        )
        self.assertEqual(self.jitter.call_args_list, [call(0, 10)] * 4)
        self.assertIn("Retrying in 5.5 second(s)", self.stderr.getvalue())

    def test_final_failure_is_preserved_without_another_delay(self):
        errors = (self.http_error(503), URLError("offline"), TimeoutError("timed out"))
        for error in errors:
            with self.subTest(error=error):
                if isinstance(error, HTTPError):
                    self.addCleanup(error.close)
                self.urlopen.reset_mock()
                self.sleep.reset_mock()
                self.jitter.reset_mock()
                self.stderr.seek(0)
                self.stderr.truncate()
                self.urlopen.side_effect = error

                with self.assertRaises(type(error)) as raised:
                    _open_download_url("url")

                self.assertIs(raised.exception, error)
                self.assertEqual(self.urlopen.call_count, 5)
                self.assertEqual(self.sleep.call_count, 4)
                self.assertEqual(self.jitter.call_count, 4)
                self.assertEqual(self.stderr.getvalue().count("Retrying"), 4)


if __name__ == "__main__":
    unittest.main()
