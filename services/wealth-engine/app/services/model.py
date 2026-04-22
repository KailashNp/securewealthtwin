import numpy as np
from sklearn.ensemble import RandomForestClassifier
import shap

# Dummy training data (for demo)
X = np.array([
    [0.1, 0.2, 1],
    [0.3, 0.8, 0],
    [0.15, 0.3, 1],
    [0.4, 0.9, 0],
])

y = np.array([1, 0, 1, 0])  # 1 = needs improvement, 0 = good

model = RandomForestClassifier()
model.fit(X, y)

explainer = shap.TreeExplainer(model)


def predict_and_explain(profile):
    features = np.array([[
        profile.savings_rate,
        profile.tax_usage,
        1 if profile.expenses_pattern == "unstable" else 0
    ]])

    prediction = model.predict(features)[0]
    shap_values = explainer.shap_values(features)

    return prediction, shap_values, features