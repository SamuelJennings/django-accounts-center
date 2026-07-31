from django.apps import AppConfig


class TestappConfig(AppConfig):
    """The suite's second Account Center integration.

    A plain installed app, not a ``dac.*`` package — the core package knows
    nothing about it. It exists to prove that an outside app can contribute
    gated menu entries and serve a management page through the shared
    ``dac/base.html`` layout, which a suite with only ``dac.allauth`` cannot
    express.
    """

    name = "tests.testapp"
    label = "testapp"
    verbose_name = "Test integration"
