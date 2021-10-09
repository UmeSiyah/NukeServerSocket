import os
import configparser
from typing import List
import pytest
from PySide2.QtWidgets import QCheckBox, QWidget

from src.widgets import settings_widget


class TestSubStateSettings:
    settings_widget: QWidget

    @property
    def output_console(self) -> QCheckBox:
        return self.settings_widget._output_console

    @property
    def format_output(self) -> QCheckBox:
        return self.settings_widget._format_output

    @property
    def clear_text(self) -> QCheckBox:
        return self.settings_widget._clear_output

    def test_output_console_is_true(self, setup_no_settings):
        """If `console_output` is enable, so it should be for `clear_text` and 
        `format_output`.
        """
        self.settings_widget = settings_widget.SettingsWidget()

        self.output_console.setChecked(True)

        assert self.clear_text.isChecked()
        assert self.format_output.isChecked()

    def test_output_console_is_false(self, setup_no_settings):
        """If `console_output` is disabled, so it should be for `clear_text` and 
        `format_output`.
        """
        def is_sub_state_false():
            assert not self.clear_text.isChecked()
            assert not self.format_output.isChecked()
            assert not self.clear_text.isEnabled()
            assert not self.format_output.isEnabled()

        self.settings_widget = settings_widget.SettingsWidget()
        self.output_console.setChecked(False)

        is_sub_state_false()

        # when clicking nothing should happen
        self.format_output.click()
        self.clear_text.click()
        is_sub_state_false()

    def test_format_text_is_false(self, setup_no_settings):
        """If `format_text` is disabled so it should be for `clear_text`"""
        def is_sub_state_false():
            assert not self.clear_text.isEnabled()
            assert not self.clear_text.isChecked()

        self.settings_widget = settings_widget.SettingsWidget()
        self.output_console.setChecked(True)
        self.format_output.setChecked(False)

        is_sub_state_false()

        # when clicking nothing should happen
        self.clear_text.click()
        is_sub_state_false()


class TestSettingsFile:
    settings_widget: QWidget

    @property
    def checkboxes(self) -> List[QCheckBox]:
        return self.settings_widget.findChildren(QCheckBox)

    def test_no_settings_default_values(self, setup_no_settings):
        """Check if checkbox values are on the default if no ini file is found."""
        initial_values = {
            'output_to_console': True,
            'format_text': True,
            'clear_output': True,
            'override_input_editor': False,
            'show_file_path': False,
            'show_unicode': True,
        }
        self.settings_widget = settings_widget.SettingsWidget()

        checkbox: QCheckBox
        for checkbox in self.checkboxes:
            value = initial_values[checkbox.objectName()]
            assert checkbox.isChecked() == value

    @pytest.fixture()
    def setup_fake_config_file(self, setup_no_settings):
        """Write options state to fake config file"""

        self.settings_widget = settings_widget.SettingsWidget()

        checkbox: QCheckBox
        for checkbox in self.checkboxes:
            checkbox.toggle()
            checkbox.setChecked(True)

    def test_settings_exists(self, setup_fake_config_file, fake_settings_file):
        """Check if file settings was created."""
        assert os.path.exists(fake_settings_file)

    def test_check_value(self, setup_fake_config_file, fake_settings_file):
        """Check if file checkboxes saved their state on the file settings"""

        config = configparser.ConfigParser()
        config.read(fake_settings_file)

        settings_values = config['options']

        for opt in settings_values:
            assert config.getboolean('options', opt)
