# coding:utf-8
"""
=====================================
Inference for Dynamic Linear Systems
=====================================

# features
* estimate current state
* predict after k step state
* predict after k step observation

"""
import numpy as np


class KalmanFilter(object):
    """カルマンフィルタの実装
        * p(z_{n+1}|z_{n}) = N(z_{n+1}|F z_{n},\gamma)
        * p(x_{n}|z_{n}) = N(x_{n}|C z_{n},\sigma)

    Parameters
    ----------
    transition_matrix : ndarray, shape = (state_dim, state_dim)

    observation_matrix : ndarray, shape = (observation_dim, state_dim)

    process_noise : ndarray, shape = (state_dim, state_dim)
        also known as process_covariance_matrix.

    observation_noise : ndarray, shape = (observation_dim, ovservation_dim)
        also known as observation_covariance_matrix.
    """

    def __init__(self, transition_matrix, observation_matrix, process_noise, observation_noise):
        self.F = transition_matrix  # 遷移行列
        self.H = observation_matrix  # 観測行列

        self.Q = process_noise  # プロセスノイズの分散共分散行列
        self.R = observation_noise  # 観測ノイズの分散共分散行列

        self.m = np.random.normal(size=4)  # 状態量の条件付き期待値
        self.P = np.eye(4)  # 推定誤差分散共分散行列

        self.K = None  # カルマンゲイン

        self.M = self.F.shape[0]  # 状態量の次元数
        self.N = self.H.shape[0]  # 観測値の次元数

    @property
    def state_dim(self):
        return self.M

    @property
    def observation_dim(self):
        return self.N

    @property
    def current_state(self):
        return self.m, self.P

    @property
    def transition_matrix(self):
        return self.F

    @property
    def observation_matrix(self):
        return self.H

    @property
    def process_noise(self):
        return self.Q

    @property
    def observation_noise(self):
        return self.R

    def update(self, observerd_data):
        """ update state

        推定した状態量を取得したい場合、current_stateにアクセスして下さい (← bad comment)

        Parameters
        ----------
        observerd_data : ndarray ,shape = (observation_dim)

        Returns
        -------
        self : object
            Returns the instance itself.
        """

        x = observerd_data
        F, H, Q, R = self.F, self.H, self.Q, self.R
        m = np.copy(self.m)
        P = np.copy(self.P)

        # prediction step
        m = F @ m
        P = F @ P @ F.T + Q

        # update step
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        m = m + K @ (x - H @ m)
        P = P - K @ S @ K.T

        # update parameter
        self.m = m
        self.P = P
        return self

    def predict_state(self, k, spot_estimation=False):
        """ estimate state between k step from current.

        p(z_{t+k}|x_{1:k})

        Parameters
        ----------
        k : int
            Number of prediction step.
        spot_estimation : bool
            If True, return only after k step estimate value

        Returns
        -------
        m, P : ndarrays
            The estimated value.
        """

        m = np.copy(self.m)
        P = np.copy(self.P)
        F, H, Q, R = self.F, self.H, self.Q, self.R

        estimated_mean_list = []
        estimated_covariance_list = []
        for i in range(k):
            m = F @ m
            P = F @ P @ F.T + Q

            estimated_mean_list.append(np.copy(m))
            estimated_covariance_list.append(np.copy(P))

        if spot_estimation:
            return estimated_mean_list[-1], estimated_covariance_list[-1]
        else:
            return estimated_mean_list, estimated_covariance_list

    def predict_observation(self, k, spot_estimation=False):
        """ estimate observation between k step from current.

        p(x_{t+k}|x_{1:k})

        Parameters
        ----------
        k : int
            Number of prediction step.
        spot_estimation : bool
            If True, return only after k step estimate value

        Returns
        -------
        predicted_x, predicted_R : ndarrays
            The estimated value.
        """

        F, H, Q, R = self.F, self.H, self.Q, self.R
        estimated_state_data = self.predict_state(k)

        estimated_mean_list = []
        estimated_covariance_list = []

        for i in range(k):
            m = estimated_state_data[0][i]
            P = estimated_state_data[1][i]

            predicted_x = H @ m
            predicted_R = H @ P @ H.T + R

            estimated_mean_list.append(predicted_x)
            estimated_covariance_list.append(predicted_R)

        if spot_estimation:
            return estimated_mean_list[-1], estimated_covariance_list[-1]
        else:
            return estimated_mean_list, estimated_covariance_list
