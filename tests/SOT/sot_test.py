from dataclasses import asdict
from re import I

import numpy as np
import pytest

from mot.common.gaussian_density import GaussianDensity as Gaussian
from mot.configs import GroundTruthConfig, SensorModelConfig
from mot.measurement_models import (
    ConstantVelocityMeasurementModel,
    RangeBearingMeasurementModel,
)
from mot.motion_models import ConstantVelocityMotionModel, CoordinateTurnMotionModel
from mot.scenarios.scenario_configs import linear_sot, nonlinear_sot
from mot.simulator import MeasurementData, ObjectData
from mot.trackers.single_object_trackers.nearest_neighbour_tracker import (
    NearestNeighbourTracker,
)
from mot.utils.get_path import delete_images_dir, get_images_dir
from mot.utils.visualizer import Animator, Plotter


@pytest.mark.parametrize(
    "config, motion_model, meas_model, name, tracker_initial_state",
    [
        (
            linear_sot,
            ConstantVelocityMotionModel,
            ConstantVelocityMeasurementModel,
            "SOT linear case (CV)",
            Gaussian(means=np.array([-40, -40, 15.0, 5.0]), covs=100.0 * np.eye(4)),
        ),
        # (
        #     nonlinear_sot,
        #     CoordinateTurnMotionModel,
        #     RangeBearingMeasurementModel,
        #     "SOT non linear case (CT)",
        #     Gaussian(
        #         means=np.array([0, 0, 10, 0, np.pi / 180]),
        #         covs=np.power(np.diag([1, 1, 1, 1 * np.pi / 180, 1 * np.pi / 180]), 2),
        #     ),
        # ),
    ],
)
@pytest.mark.parametrize("tracker", [(NearestNeighbourTracker)])  # noqa
def test_tracker(config, motion_model, meas_model, name, tracker, tracker_initial_state):
    config = asdict(config)
    ground_truth = GroundTruthConfig(**config)
    motion_model = motion_model(**config)
    sensor_model = SensorModelConfig(**config)
    meas_model = meas_model(**config)

    object_data = ObjectData(ground_truth_config=ground_truth, motion_model=motion_model, if_noisy=False)
    meas_data = MeasurementData(object_data=object_data, sensor_model=sensor_model, meas_model=meas_model)

    # Single object tracker parameter setting
    P_G = 0.999  # gating size in percentage

    tracker = tracker(
        meas_model=meas_model,
        sensor_model=sensor_model,
        motion_model=motion_model,
        gating_size=P_G,
        initial_state=tracker_initial_state,
    )
    tracker_estimations = []
    for timestep in range(ground_truth.total_time):
        timestep, measurements, sources = next(meas_data)
        estimations = tracker.step(measurements)
        tracker_estimations.append(estimations)

    Plotter.plot(
        [object_data, meas_data, tracker_estimations],
        out_path=get_images_dir(__file__) + "/" + name + ".png",
    )

    # Animator.animate(
    #     [meas_data[1], object_data, tracker_estimations],
    #     title=name,
    #     filename=get_images_dir(__file__) + "/" + name + ".gif",
    # )
