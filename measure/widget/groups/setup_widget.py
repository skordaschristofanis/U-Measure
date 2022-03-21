import os
from qtpy.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QAbstractSpinBox,
)
from qtpy.QtCore import Qt

from measure.util import qss_path


class SetupWidget(QGroupBox):
    """Setup widget groupbox to be used in the MainWidget."""

    _qss = os.path.join(qss_path, "setup_group.qss")

    def __init__(self) -> None:
        super(SetupWidget, self).__init__()

        # Initialize setup group's widgets
        self._lbl_mso = QLabel("MSO")
        self._lbl_afg = QLabel("AFG")
        self._lbl_run_number = QLabel("#Run")
        self._lbl_vpp = QLabel("Vpp")
        self.lbl_path = QLabel("test")
        self.txt_mso = QLineEdit()
        self.txt_afg = QLineEdit()
        self.txt_run_number = QLineEdit()
        self.spin_vpp = QDoubleSpinBox()
        self.btn_reset = QPushButton("Reset")

        # List of setup group's widgets
        self._setup_widgets = [
            self._lbl_mso,
            self._lbl_afg,
            self._lbl_run_number,
            self._lbl_vpp,
            self.txt_mso,
            self.txt_afg,
            self.txt_run_number,
            self.spin_vpp,
            self.btn_reset,
        ]

        # Run setup group's widget methods
        self._configure_setup_group()
        self._configure_setup_labels()
        self._configure_setup_text_boxes()
        self._configure_setup_spin_boxes()
        self._configure_setup_buttons()
        self._layout_setup_widgets()

    def disable(self) -> None:
        """Disables all setup group's widgets."""
        [widget.setEnabled(False) for widget in self._setup_widgets]

    def enable(self) -> None:
        """Enables all setup group's widgets."""
        [widget.setEnabled(True) for widget in self._setup_widgets]

    def _configure_setup_group(self) -> None:
        """Configuration of the setup groupbox."""
        # Set group object name
        self.setObjectName("group-setup")

        # Set the stylesheet from assets/qss/setup_group.qss
        self.setStyleSheet(open(self._qss, "r").read())

    def _configure_setup_labels(self) -> None:
        """Configuration of the setup group's labels."""
        labels = [
            self._lbl_mso,
            self._lbl_afg,
            self._lbl_run_number,
            self._lbl_vpp,
            self.lbl_path,
        ]
        [label.setObjectName("lbl-setup") for label in labels]
        self.lbl_path.setObjectName("lbl-path")

    def _configure_setup_text_boxes(self) -> None:
        """Configuration of the setup group's text boxes."""
        txt_boxes = [self.txt_mso, self.txt_afg, self.txt_run_number]
        [txt_box.setObjectName("txt-setup") for txt_box in txt_boxes]

    def _configure_setup_spin_boxes(self) -> None:
        """Configuration of the setup group's spin boxes."""
        self.spin_vpp.setObjectName("spin-vpp")
        self.spin_vpp.setMinimum(0.0)
        self.spin_vpp.setMaximum(5.0)
        self.spin_vpp.setSingleStep(0.1)
        self.spin_vpp.setDecimals(1)
        self.spin_vpp.setAlignment(Qt.AlignCenter)
        self.spin_vpp.setButtonSymbols(QAbstractSpinBox.NoButtons)

    def _configure_setup_buttons(self) -> None:
        """Configuration of the setup group's buttons."""
        self.btn_reset.setObjectName("btn-reset")
        self.btn_reset.setFlat(True)
        self.btn_reset.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _layout_setup_widgets(self) -> None:
        """Sets the layout for the setup group widgets."""
        # Main setup layout widget
        setup_layout = QGridLayout()
        setup_layout.setContentsMargins(0, 0, 0, 0)

        # layout for mso widgets
        mso_layout = QHBoxLayout()
        mso_layout.setContentsMargins(0, 0, 0, 0)
        mso_layout.setSpacing(7)
        mso_layout.addWidget(self._lbl_mso)
        mso_layout.addWidget(self.txt_mso)
        setup_layout.addLayout(mso_layout, 0, 0, 1, 6)

        # layout for afg widgets
        afg_layout = QHBoxLayout()
        afg_layout.setContentsMargins(0, 0, 0, 0)
        afg_layout.setSpacing(13)
        afg_layout.addWidget(self._lbl_afg)
        afg_layout.addWidget(self.txt_afg)
        setup_layout.addLayout(afg_layout, 1, 0, 1, 6)

        # layout for #run and vpp widgets
        run_vpp_layout = QHBoxLayout()
        run_vpp_layout.setContentsMargins(0, 0, 0, 0)
        run_vpp_layout.addWidget(self._lbl_run_number)
        run_vpp_layout.addWidget(self.txt_run_number)
        run_vpp_layout.addWidget(self._lbl_vpp)
        run_vpp_layout.addWidget(self.spin_vpp)
        run_vpp_layout.addStretch(1)
        setup_layout.addLayout(run_vpp_layout, 2, 0, 1, 4)

        # layout for path widgets
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(self.lbl_path)
        path_layout.addStretch(1)
        setup_layout.addLayout(path_layout, 3, 0, 1, 4)

        # layout for reset widgets
        reset_layout = QHBoxLayout()
        reset_layout.setContentsMargins(0, 0, 0, 0)
        reset_layout.addStretch(1)
        reset_layout.addWidget(self.btn_reset)
        setup_layout.addLayout(reset_layout, 2, 4, 2, 2)

        self.setLayout(setup_layout)