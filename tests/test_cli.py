from tests.support import ShelfTestCase


class AddCommandTest(ShelfTestCase):
    def test_add_prints_the_new_book(self):
        result = self.shelf("add", "Dune", "Frank Herbert")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Added #1 [to-read] Dune by Frank Herbert\n")

    def test_add_writes_to_shelf_path_and_not_to_home(self):
        self.shelf("add", "Dune", "Frank Herbert")

        self.assertTrue(self.shelf_path.exists())
        self.assertFalse((self.home / ".shelf.json").exists())


class ListCommandTest(ShelfTestCase):
    def test_an_empty_shelf_explains_how_to_add_a_book(self):
        result = self.shelf("list")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Your shelf is empty", result.stdout)

    def test_list_shows_every_book_in_id_order(self):
        self.shelf("add", "Dune", "Frank Herbert")
        self.shelf("add", "Kindred", "Octavia E. Butler", "--status", "reading")

        result = self.shelf("list")

        self.assertEqual(result.stdout.splitlines(), [
            "#1 [to-read] Dune by Frank Herbert",
            "#2 [reading] Kindred by Octavia E. Butler",
        ])

    def test_status_shows_only_matching_books_in_list_order(self):
        self.shelf("add", "Dune", "Frank Herbert", "--status", "reading")
        self.shelf("add", "Emma", "Jane Austen")
        self.shelf("add", "Kindred", "Octavia E. Butler", "--status", "reading")
        self.shelf("add", "Beloved", "Toni Morrison", "--status", "done")
        expected = {
            "to-read": "#2 [to-read] Emma by Jane Austen\n",
            "reading": (
                "#1 [reading] Dune by Frank Herbert\n"
                "#3 [reading] Kindred by Octavia E. Butler\n"
            ),
            "done": "#4 [done] Beloved by Toni Morrison\n",
        }

        for status, output in expected.items():
            with self.subTest(status=status):
                result = self.shelf("list", "--status", status)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, output)

    def test_status_without_matches_says_so(self):
        self.shelf("add", "Dune", "Frank Herbert")

        result = self.shelf("list", "--status", "done")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "No books with status done.\n")

    def test_status_on_an_empty_shelf_says_no_books_match(self):
        result = self.shelf("list", "--status", "reading")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "No books with status reading.\n")

    def test_an_invalid_status_is_a_usage_error_naming_the_valid_values(self):
        result = self.shelf("list", "--status", "bad")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        # The usage text also names the values, so check only the error itself.
        _, found, error = result.stderr.partition("shelf list: error: ")
        self.assertTrue(found, result.stderr)
        self.assertIn("invalid choice: 'bad'", error)
        for status in ("to-read", "reading", "done"):
            self.assertIn(status, error)


class StartAndFinishCommandTest(ShelfTestCase):
    def test_start_then_finish_a_book(self):
        self.shelf("add", "Dune", "Frank Herbert")

        started = self.shelf("start", "1")
        finished = self.shelf("finish", "1")

        self.assertEqual(started.stdout, "Started #1 [reading] Dune by Frank Herbert\n")
        self.assertEqual(finished.stdout, "Finished #1 [done] Dune by Frank Herbert\n")

    def test_an_unknown_id_is_an_error(self):
        result = self.shelf("finish", "42")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "shelf: error: no book with id 42\n")


class UsageTest(ShelfTestCase):
    def test_a_missing_command_is_a_usage_error(self):
        result = self.shelf()

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: shelf", result.stderr)
