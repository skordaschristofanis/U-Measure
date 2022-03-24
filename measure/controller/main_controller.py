import datetime
import sys

from qtpy.QtWidgets import QApplication, QMessageBox
from qtpy.QtCore import QSettings, QObject, Signal, QTimer

from measure.widget import MainWidget
from measure.widget.custom import MsgBox
from measure.util import GUIWorker
from measure.controller import SetupController, ExperimentController, VisaController


class MainController(QObject):
    """Used to connect all controllers, models and widgets."""

    collect_triggered: Signal = Signal()
    abort_triggered: Signal = Signal()
    finished: Signal = Signal()

    def __init__(self) -> None:
        super(MainController, self).__init__()
        self._app = QApplication(sys.argv)
        self._settings = QSettings("GSECARS", "U-Measure")
        self._widget = MainWidget(settings=self._settings)

        # Setup controller
        self._setup_controller = SetupController(
            widget=self._widget.group_widget.setup,
            settings=self._settings
        )

        # Experiment controller
        self._experiment_controller = ExperimentController(
            widget=self._widget.group_widget.experiment,
            settings=self._settings
        )

        # Visa controller
        self._visa_controller = VisaController(
            setup_model=self._setup_controller.model,
            experiment_model=self._experiment_controller.model,
            basedir=self._setup_controller.basedir,
        )

        # Thread and timer
        self._main_timer = QTimer()
        self._main_timer.setInterval(30)
        self._main_worker = GUIWorker(self._worker_process, ())
        self._main_worker.start()

        self._start_time = None

        self._configure_widgets()
        self._connect_widgets()

        self._collecting = False
        self._aborting = False
        self._input_check_passed = True

    def _configure_widgets(self) -> None:
        """Sets some configuration values before opening the main application window."""
        # Set initial focus
        self._widget.group_widget.setup.lbl_path.setFocus()

    def _connect_widgets(self) -> None:
        self._visa_controller.new_feedback_message.connect(self._visa_controller_message)
        self._visa_controller.current_repetition.connect(self._change_current_repetition)

        self._main_timer.timeout.connect(self._timer_ticks)
        self._widget.group_widget.control_status.btn_collection.clicked.connect(
            self._btn_collection_clicked
        )
        self.collect_triggered.connect(self._change_to_collecting)
        self.abort_triggered.connect(self._change_to_aborting)
        self.finished.connect(self._change_to_idle)

    def disable_widgets(self) -> None:
        self._widget.group_widget.setup.disable()
        self._widget.group_widget.experiment.disable()

    def enable_widgets(self) -> None:
        self._widget.group_widget.setup.enable()
        self._widget.group_widget.experiment.enable()

    def _timer_ticks(self) -> None:
        elapsed_time = datetime.datetime.now() - self._start_time
        current_delta = datetime.timedelta(seconds=elapsed_time.seconds)
        self._widget.group_widget.control_status.lbl_time.setText(str(current_delta))

    def _change_to_collecting(self) -> None:
        self.disable_widgets()

        self._append_feedback(message="Starting new collection process.")

        self._widget.group_widget.control_status.lbl_status.setText("Collecting")
        self._widget.group_widget.control_status.btn_collection.setText("Abort")

        self._widget.group_widget.control_status.lbl_status.setEnabled(False)
        self._widget.group_widget.control_status.lbl_time.setEnabled(False)
        self._widget.group_widget.control_status.lbl_repetition_status.setEnabled(False)

        self._widget.group_widget.control_status.lbl_repetition_status.setVisible(True)

    def _change_to_idle(self) -> None:
        self.enable_widgets()
        self._aborting = False
        self._collecting = False

        self._widget.group_widget.control_status.lbl_status.setText("Idle")
        self._widget.group_widget.control_status.btn_collection.setText("Collect")

        self._widget.group_widget.control_status.lbl_status.setEnabled(True)
        self._widget.group_widget.control_status.lbl_time.setEnabled(True)
        self._widget.group_widget.control_status.lbl_repetition_status.setEnabled(True)

        self._widget.group_widget.control_status.lbl_repetition_status.setVisible(False)

        self._main_timer.stop()

    def _change_to_aborting(self) -> None:
        self._widget.group_widget.control_status.lbl_status.setText("Aborting")
        self._aborting = True

    def _change_current_repetition(self, repetition: int) -> None:
        self._widget.group_widget.control_status.lbl_repetition_status.setText(
            f"{repetition}/{self._experiment_controller.model.repetitions}"
        )

    def _check_for_empty_txt_boxes(self, field_name: str, text: str) -> bool:
        """Looks for empty text boxes."""
        if text.strip() == "":
            message = f"The {field_name} field can't be empty. Please try again."
            self._append_feedback(message)
            MsgBox(msg=message)

            self._input_check_passed = False

        return self._input_check_passed

    def _check_for_valid_ip(self, field_name: str, ip: str) -> bool:
        sections = ip.split(".")

        if len(sections) != 4:
            self._input_check_passed = False

        for section in sections:
            if not isinstance(int(section), int):
                self._input_check_passed = False

            if int(section) < 0 or int(section) > 255:
                self._input_check_passed = False

        if not self._input_check_passed:
            message = f"The {field_name} must be a valid IPv4. Please try again."
            self._append_feedback(message)
            MsgBox(msg=message)

        return self._input_check_passed

    def _check_input_before_collection(self) -> None:

        if not self._check_for_empty_txt_boxes(
            field_name="MSO",
            text=self._setup_controller.model.mso
        ):
            return None

        if not self._check_for_empty_txt_boxes(
            field_name="AFG",
            text=self._setup_controller.model.afg
        ):
            return None

        if not self._check_for_empty_txt_boxes(
            field_name="Cycle",
            text=self._setup_controller.model.cycle
        ):
            return None

        if not self._check_for_empty_txt_boxes(
            field_name="#Run",
            text=self._setup_controller.model.run_number
        ):
            return None

        if not self._check_for_empty_txt_boxes(
            field_name="Threshold",
            text=str(self._experiment_controller.model.threshold)
        ):
            return None

        if self._experiment_controller.model.repetitions > 1:
            if not self._check_for_empty_txt_boxes(
                field_name="Scan",
                text=self._experiment_controller.model.scan
            ):
                return None

        if not self._check_for_valid_ip(
            field_name="MSO",
            ip=self._setup_controller.model.mso
        ):
            return None

        if not self._check_for_valid_ip(
            field_name="AFG",
            ip=self._setup_controller.model.afg
        ):
            return None

    def _btn_collection_clicked(self) -> None:

        if self._collecting:
            self.abort_triggered.emit()
            return None

        self._input_check_passed = True
        self._check_input_before_collection()

        if not self._input_check_passed:
            return None

        bold = u"\033[1m"
        bold_close = ""
        _msg_question = QMessageBox.question(
            self._widget, "Collection confirmation",
            f"The load and temperature of the experiment are {self._experiment_controller.model.load}\033[0m\nI tons and\n"
            f"{self._experiment_controller.model.temperature} K, respectively.\n\n"
            f"Are you sure you want to continue with the collection?"
        )

        if _msg_question != QMessageBox.Yes:
            return None

        self.collect_triggered.emit()
        self._start_time = datetime.datetime.now()
        self._main_timer.start(100)
        self._collecting = True
        self._main_timer.start()

    def _worker_process(self) -> None:

        while not self._widget.terminated:

            if self._collecting:
                self._visa_controller.connect()
                self._visa_controller.collect_data(abort_status=self._aborting)
                self.finished.emit()

            self._visa_controller.restore_defaults()

    def _visa_controller_message(self, message: str):
        self._append_feedback(message=message)

    def _append_feedback(self, message: str):
        self._widget.group_widget.control_status.txt_feedback.appendPlainText(
            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - {message}"
        )

    def run(self) -> None:
        """Starts the application."""
        self._widget.display(
            window_size=self._settings.value("window_size"),
            window_position=self._settings.value("window_position")
        )
        sys.exit(self._app.exec())
