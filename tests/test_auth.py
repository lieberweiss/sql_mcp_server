from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
import unittest

from sql_mcp_server.auth import ApiPrincipal, AuthManager


class AuthManagerTests(unittest.TestCase):
    def test_parse_valid_keys(self) -> None:
        manager = AuthManager("alice:token123:rwad,bob:tok456:rw")

        principal = manager.authenticate("token123")

        self.assertEqual(principal.username, "alice")
        self.assertEqual(principal.scopes, {"r", "w", "a", "d"})

        principal_rw = manager.authenticate("tok456")
        self.assertEqual(principal_rw.scopes, {"r", "w"})

    def test_unknown_scope_is_ignored(self) -> None:
        manager = AuthManager("eve:badtoken:rwx")

        principal = manager.authenticate("badtoken")

        self.assertEqual(principal.scopes, {"r", "w"})

    def test_authentication_required(self) -> None:
        manager = AuthManager("alice:token123:r")

        with self.assertRaises(Exception):
            manager.authenticate(None)

    def test_invalid_token(self) -> None:
        manager = AuthManager("alice:token123:r")

        with self.assertRaises(Exception):
            manager.authenticate("wrong")

    def test_reload_keys_when_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            keys_path = Path(tmpdir) / "tokens.txt"
            keys_path.write_text("alice:token123:r\n", encoding="utf-8")

            manager = AuthManager(keys_path=keys_path)
            principal = manager.authenticate("token123")
            self.assertEqual(principal.username, "alice")

            self.assertTrue(manager.enabled)

            keys_path.write_text("bob:tok456:rw\n", encoding="utf-8")
            now = time.time() + 1.0
            os.utime(keys_path, (now, now))

            principal_updated = manager.authenticate("tok456")
            self.assertEqual(principal_updated.username, "bob")


if __name__ == "__main__":
    unittest.main()
