# coding:utf-8
"""
# カルマンフィルタの実装

## モデル
    状態方程式
        * p(z_{n+1}|z_{n}) = N(z_{n+1}|F z_{n},\gamma)= N(z_{n+1}|n_{n},\gamma)
    観測方程式
        * p(x_{n}|z_{n}) = N(x_{n}|C z_{n},\sigma) = N(x_{n}|z_{n},\sigma)
## 機能
    * 状態推定(フィルタリング)
    * 状態予測
    * 観測値の予測
"""

import numpy as np
import matplotlib.pyplot as plt


class KalmanFilter(object):
    def __init__(self, dim_x, dim_z):
        self.F = None  # 遷移行列
        self.H = None  # 観測行列

        self.Q = None  # プロセスノイズの分散共分散行列
        self.R = None  # 観測ノイズの分散共分散行列

        self.K = None  # カルマンゲイン
        self.m = None  # 状態推定値
        self.P = None  # 推定誤差分散共分散行列

    @property
    def get_state(self):
        return self.m, self.P

    @property
    def transition_matrix(self):
        return self.F

    @property
    def observation_matrix(self):
        return self.H

    @property
    def process_covariance_matrix(self):
        return self.Q

    @property
    def observation_covariance_matrix(self):
        return self.R

    def update(self, observerd_data):
        """
        p(z_{t}|x_{1:t})
        観測されたデータに応じて、状態と推定共分散行列を更新する
        :param 観測値 (1d ndarray)
        :return: 状態の確率密度関数の平均値と分散
        """

        x = observerd_data
        F, H = self.F, self.H
        Q, R = self.Q, self.R
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

    def predict_state(self, k):
        # p(z_{t+k}|x_{1:k})
        # estimate state after k step
        pass

    def predict_observation(self, k):
        # p(x_{t+k}|x_{1:k})
        # estimate observation after k step

        pass


if __name__ == "__main__":
    dt = 10 ** -1
    sigma1 = 0.5
    sigma2 = 0.5
    q1 = 0.5
    q2 = 0.5
    # transition matrix
    A = np.array([[1, 0, dt, 0],
                  [0, 1, 0, dt],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])

    # process noise covariance
    Q = np.array([[q1 * dt ** 3 / 3, 0, q1 * dt ** 2 / 2, 0],
                  [0, q1 * dt ** 3 / 3, 0, q2 * dt ** 2 / 2],
                  [q1 * dt ** 2 / 2, 0, q1 * dt, 0],
                  [0, q2 * dt ** 2 / 2, 0, q2 * dt]])

    # observe matrix
    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])
    # measurement noise covariance
    R = np.array([[sigma1 ** 2, 0],
                  [0, sigma2 ** 2]])

    m = np.random.normal(size=4)
    P = np.eye(4) * 10

    # set parameter
    kf = KalmanFilter(4, 2)

    kf.F = A
    kf.H = H

    kf.Q = Q
    kf.R = R

    kf.m = m
    kf.P = P

    t = np.linspace(0, 30, 1000)
    trajectory = np.c_[np.cos(t) + t, np.sin(t) * t]

    trajectory += np.random.normal(0, 1, size=trajectory.shape)
    state_list = []
    var_list = []

    for y in trajectory:
        kf.update(y)
        m, P = kf.get_state
        state_list.append(np.copy(m))
        var_list.append(np.copy(P[0, 0]))

    X = np.array(state_list)
    v = np.array(var_list)

    plt.scatter(X[:, 0], X[:, 1], s=v ** 0.5 * 10, alpha=0.25)

    plt.plot(trajectory[:, 0], trajectory[:, 1], "bo", label="observerd")
    plt.plot(X[:, 0], X[:, 1], "r-", linewidth=5, label="estimated")
    plt.legend()

    plt.show()
