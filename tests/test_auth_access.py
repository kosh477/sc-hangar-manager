import unittest

from app.main import create_app


class AuthAccessTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def _assert_unauthorized(self, method: str, path: str):
        response = self.client.open(path, method=method)
        self.assertEqual(response.status_code, 401, f"{method} {path} should require auth")

    def test_public_endpoints(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_protected_api_endpoints_require_auth(self):
        protected = [
            ("GET", "/users"),
            ("GET", "/ships"),
            ("POST", "/ships"),
            ("GET", "/ship/1/parts"),
            ("POST", "/ship/1/parts"),
            ("GET", "/user/1/ships"),
            ("POST", "/user/1/ships"),
            ("GET", "/user/1/parts"),
            ("POST", "/user/1/parts"),
            ("GET", "/parts"),
            ("POST", "/parts"),
            ("GET", "/part-types"),
            ("POST", "/part-types"),
        ]
        for method, path in protected:
            with self.subTest(method=method, path=path):
                self._assert_unauthorized(method, path)

    def test_protected_ui_endpoints_require_auth(self):
        protected_pages = [
            "/ui/user/1/ships",
            "/ui/user/1/parts",
            "/ui/ship/1",
            "/ui/parts-catalog",
        ]
        for path in protected_pages:
            with self.subTest(path=path):
                self._assert_unauthorized("GET", path)


if __name__ == "__main__":
    unittest.main()
