# Introduction to pytest-textual-snapshot

`pytest-textual-snapshot` is a pytest plugin for snapshot testing of Textual applications. It works by saving an SVG screenshot of a running Textual app to disk. The next time the test runs, it takes another screenshot and compares it to the saved one.

## Basic Usage

To use `pytest-textual-snapshot`, you need to inject the `snap_compare` fixture into your test. You can then call it with an instance of your Textual app.

Here is a basic example:

```python
from textual.app import App

class MyApp(App):
    ...

def test_my_app_snapshot(snap_compare):
    app = MyApp()
    assert snap_compare(app)
```

The first time you run this test, it will save a snapshot of your application's UI to a file. On subsequent runs, it will compare the current UI with the saved snapshot. If they don't match, the test will fail.

## Updating Snapshots

If you make intentional changes to your app's UI, you'll need to update the snapshots. You can do this by running pytest with the `--snapshot-update` flag:

```bash
pytest --snapshot-update
```

This will overwrite the existing snapshots with the new version of your app's UI.

## Windows Usage

There are no special considerations for using `pytest-textual-snapshot` on Windows. It should work the same as on other operating systems.

## Resources

*   [GitHub Repository](https://github.com/Textualize/pytest-textual-snapshot)
*   [PyPI Page](https://pypi.org/project/pytest-textual-snapshot/)
*   [Textual Testing Documentation](https://textual.textualize.io/guide/testing/)