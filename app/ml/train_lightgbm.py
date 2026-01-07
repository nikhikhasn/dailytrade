import joblib
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.ml.build_features import build_features


FEATURE_COLS = [
    "range_lag1",
    "volatility_lag1",
    "volume_lag1",
    "range_mean_3",
    "range_std_3",
]


def train_model(target_col, model_name):
    df = build_features()

    X = df[FEATURE_COLS]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, shuffle=False
    )

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=26,
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"{model_name} accuracy: {acc:.3f}")

    joblib.dump(model, f"app/ml/models/{model_name}.joblib")


if __name__ == "__main__":
    train_model("low_bucket", "buy_time_model")
    train_model("high_bucket", "sell_time_model")
