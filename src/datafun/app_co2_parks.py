"""app_co2_parks.py - CO2 regression (log version)

Purpose:
- Explore relationship between GDP and CO2 emissions
- Use log transformation to handle skewed real-world data
- Fit and visualize linear regression
"""

from typing import Final

from datafun_toolkit.logger import get_logger, log_header
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression

LOG = get_logger("P07", level="DEBUG")
log_header(LOG, "P07")

DATASET_NAME: Final[str] = "owid-co2-data-subset.csv"

# ORIGINAL variables
FEATURE_COL: Final[str] = "gdp"
TARGET_COL: Final[str] = "co2"

# LOG TRANSFORM VARIABLES (THIS IS THE KEY CHANGE)
X_COL_LOG = "log_gdp"
Y_COL_LOG = "log_co2"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(f"data/raw/{DATASET_NAME}")
    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop missing + apply log transform"""

    df_model = df[[FEATURE_COL, TARGET_COL]].dropna().copy()

    # remove zeros/negatives (log can't handle them)
    df_model = df_model[(df_model[FEATURE_COL] > 0) & (df_model[TARGET_COL] > 0)]

    # LOG TRANSFORMATION (this is the "new regression idea")
    df_model[X_COL_LOG] = np.log10(df_model[FEATURE_COL])
    df_model[Y_COL_LOG] = np.log10(df_model[TARGET_COL])

    return df_model


def build_xy(df_model: pd.DataFrame):
    X = df_model[[X_COL_LOG]].to_numpy()
    y = df_model[Y_COL_LOG].to_numpy()
    return X, y


def fit_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model


def make_plots(df_model, model):
    X = df_model[[X_COL_LOG]].to_numpy()
    y = df_model[Y_COL_LOG].to_numpy()

    # predictions
    y_hat = model.predict(X)

    # sort for clean regression line
    order = np.argsort(X[:, 0])

    # === SCATTER + REGRESSION LINE ===
    plt.figure()
    sns.scatterplot(x=X[:, 0], y=y)

    plt.plot(X[order, 0], y_hat[order], color="red")

    plt.title("Log(GDP) vs Log(CO2) with Regression Line")
    plt.xlabel("log10(GDP)")
    plt.ylabel("log10(CO2)")

    # === RESIDUAL PLOT ===
    plt.figure()
    residuals = y - y_hat

    sns.scatterplot(x=X[:, 0], y=residuals)
    plt.axhline(0, color="black")

    plt.title("Residual Plot (Log Model)")
    plt.xlabel("log10(GDP)")
    plt.ylabel("Residuals")


def main():
    df = load_data()
    df_model = prepare_data(df)

    X, y = build_xy(df_model)

    model = fit_model(X, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    LOG.info(f"MODEL: log10(CO2) = {slope:.4f} * log10(GDP) + {intercept:.4f}")

    make_plots(df_model, model)

    plt.show()


if __name__ == "__main__":
    main()
