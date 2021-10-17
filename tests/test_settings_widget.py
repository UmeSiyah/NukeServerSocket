import os
import configparser

import pytest
from PySide2.QtWidgets import QCheckBox, QWidget

from src.widgets import settings_widget


@pytest.fixture()
def settings(qtbot, tmp_settings_file):

    def reset_settings():
        with open(tmp_settings_file, 'w') as _:
            pass

    widget = settings_widget.SettingsWidget()
    qtbot.addWidget(widget)

    reset_settings()

    yield widget

    reset_settings()


class TestSubStateSettings:
    settings_widget = None  # type:  QWidget

    @property
    def output_console(self):  # type: () -> QCheckBox
        return self.settings_widget._output_console

    @property
    def format_output(self):  # type: () -> QCheckBox
        return self.settings_widget._format_output

    @property
    def clear_text(self):  # type: () -> QCheckBox
        return self.settings_widget._clear_output

    def test_output_console_is_true(self, settings):
        """If `console_output` is enable, so it should be for `clear_text` and
        `format_output`.
        """
        self.settings_widget = settings

        self.output_console.setChecked(True)

        assert self.clear_text.isChecked()
        assert self.format_output.isChecked()

    def test_output_console_is_false(self, settings):
        """If `console_output` is disabled, so it should be for `clear_text` and 
        `format_output`.
        """
        def is_sub_state_false():
            assert not self.clear_text.isChecked()
            assert not self.format_output.isChecked()
            assert not self.clear_text.isEnabled()
            assert not self.format_output.isEnabled()

        self.settings_widget = settings
        self.output_console.setChecked(False)

        is_sub_state_false()

        # when clicking nothing should happen
        self.format_output.click()
        self.clear_text.click()
        is_sub_state_false()

    def test_format_text_is_false(self, settings):
        """If `format_text` is disabled so it should be for `clear_text`"""
        def is_sub_state_false():
            assert not self.clear_text.isEnabled()
            assert not self.clear_text.isChecked()

        self.settings_widget = settings
        self.output_console.setChecked(True)
        self.format_output.setChecked(False)

        is_sub_state_false()

        # when clicking nothing should happen
        self.clear_text.click()
        is_sub_state_false()


class TestSettingsFile:

    @pytest.fixture()
    def toggle_options(self, settings):
        """Toggle all options to True state."""

        for checkbox in settings.findChildren(QCheckBox):
            checkbox.toggle()
            checkbox.setChecked(True)

    def test_settings_exists(self, toggle_options, tmp_settings_file):
        """Check if file settings was created."""
        assert os.path.exists(tmp_settings_file)

    def test_check_value(self, toggle_options, tmp_settings_file):
        """Check if file checkboxes saved their state on the file settings"""

        config = configparser.ConfigParser()
        config.read(tmp_settings_file)

        settings_values = config['options']

        for opt in settings_values:
            assert config.getboolean('options', opt)

    def test_no_settings_default_values(self,  settings):
        """Check if checkbox values are on the default if no ini file is found."""

        initial_values = {
            'output_to_console': True,
            'format_text': True,
            'clear_output': True,
            'override_input_editor': False,
            'show_file_path': False,
            'show_unicode': True,
        }

        for checkbox in settings.findChildren(QCheckBox):
            value = initial_values[checkbox.objectName()]
            assert checkbox.isChecked() == value
