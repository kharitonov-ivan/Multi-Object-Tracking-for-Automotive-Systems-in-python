import os
import unittest

import matplotlib.pyplot as plt
import numpy as np

import src.utils as utils
from src.common.state import Gaussian
from src.configs import GroundTruthConfig, Object, SensorModelConfig
from src.measurement_models import ConstantVelocityMeasurementModel
from src.motion_models import ConstantVelocityMotionModel
from src.simulator import MeasurementData, ObjectData


class Test_MeasurementData(unittest.TestCase):
    def test_function_name(self):
        """Test linear model without noise"""
        # Ground truth model config
        total_time = 100
        objects_configs = [
            Object(
                initial=Gaussian(x=np.array([0.0, 0.0, 10.0, 10.0]), P=np.eye(4)),
                t_birth=0,
                t_death=total_time,
            )
        ]
        ground_truth = GroundTruthConfig(object_configs=objects_configs, total_time=total_time)

        # Linear motion model
        sigma_q = 5.0
        random_state = 42
        motion_model = ConstantVelocityMotionModel(sigma_q=sigma_q, random_state=random_state)

        # Generate true object data (noisy or noiseless) and measurement
        object_data = ObjectData(ground_truth_config=ground_truth, motion_model=motion_model, if_noisy=False)

        # Sensor model config
        P_D = 0.9  # object detection probability
        lambda_c = 10.0  # clutter rate
        range_c = np.array([[-1000, 1000], [-1000, 1000]])  # sensor range
        sensor_model = SensorModelConfig(P_D=P_D, lambda_c=lambda_c, range_c=range_c)

        # Linear measurement model
        sigma_r = 10.0
        meas_model = ConstantVelocityMeasurementModel(sigma_r=sigma_r)

        meas_data = MeasurementData(object_data=object_data, sensor_model=sensor_model, meas_model=meas_model)  # noqa F841  # noqa F841

        OUTPUT_PICTURE = "measurements.png"
        picture_path = os.path.join(utils.get_output_dir(), OUTPUT_PICTURE)  # noqa F841

        fig = plt.figure(figsize=(5, 5))  # noqa F841
        ax = plt.subplot(111, aspect="equal")
        ax.grid(which="both", linestyle="--", alpha=0.5)
