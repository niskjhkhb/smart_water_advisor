import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load data
df = pd.read_csv('ideal_water_data.csv')

# Features and target
X = df[['region', 'number_of_people']]
y = df['monthly_usage_liters']

# Create preprocessing + model pipeline
preprocessor = ColumnTransformer([
    ('region', OneHotEncoder(), ['region'])
], remainder='passthrough')

model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

# Train
model.fit(X, y)

# Save model
joblib.dump(model, 'water_usage_model2.pkl')

print("✅ Model trained and saved as water_usage_model.pkl")


