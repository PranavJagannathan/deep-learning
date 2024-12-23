# -*- coding: utf-8 -*-
"""ELnino Buoy.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ikp82lz3PdJYI9FRGb8rPPOei53WNbCK
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv("/content/elninocsv.csv")

data.interpolate(method='linear', inplace=True)

data.head()

data.tail()

data.info()

"""DATA CLEANING"""

# Strip any leading/trailing whitespace from column names
data.columns = data.columns.str.strip()

# Replace '.' with NaN for numerical conversion
columns_to_clean = ["Zonal Winds", 'Meridional Winds', 'Humidity', 'Air Temp', 'Sea Surface Temp']
for col in columns_to_clean:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    else:
        print(f"Warning: Column '{col}' not found in the dataset.")

# Display the first few rows to understand the structure of the data
print(data.head())

data = data.drop('Humidity', axis=1)

# Check for missing values
missing_values = data.isnull().sum()
print("Missing values per column:\n", missing_values)

# Summary statistics of numerical columns
print(data.describe())

# Visualization: Trend of Sea Surface Temperature over time
plt.figure(figsize=(14, 7))
data['Date'] = pd.to_datetime(data['Year'].astype(str) + '-' + data['Month'].astype(str) + '-' + data['Day'].astype(str), errors='coerce')
plt.plot(data['Date'], data['Sea Surface Temp'], label='Sea Surface Temperature', color='blue', alpha=0.6)
plt.title('Sea Surface Temperature Over Time', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Sea Surface Temperature (°C)', fontsize=14)
plt.legend()
plt.grid(True)
plt.show()

# Visualization: Distribution of Sea Surface Temperature
plt.figure(figsize=(10, 6))
sns.histplot(data['Sea Surface Temp'], kde=True, bins=30, color='blue', alpha=0.7)
plt.title('Distribution of Sea Surface Temperature', fontsize=16)
plt.xlabel('Sea Surface Temperature (°C)', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.grid(True)
plt.show()

# Visualization: Distribution of Air Temperature
plt.figure(figsize=(10, 6))
sns.histplot(data['Air Temp'], kde=True, bins=30, color='violet', alpha=0.7)
plt.title('Distribution of Air Temperature', fontsize=16)
plt.xlabel('Air Temperature (°C)', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.grid(True)
plt.show()

# Visualization: Air Temperature vs Sea Surface Temperature
plt.figure(figsize=(10, 6))
sns.scatterplot(x=data['Air Temp'], y=data['Sea Surface Temp'], alpha=0.6, color='green')
plt.title('Air Temperature vs Sea Surface Temperature', fontsize=16)
plt.xlabel('Air Temperature (°C)', fontsize=14)
plt.ylabel('Sea Surface Temperature (°C)', fontsize=14)
plt.grid(True)
plt.show()

# Scatterplot: Zonal Winds vs Meridional Winds
plt.figure(figsize=(10, 6))
sns.scatterplot(x=data['Zonal Winds'], y=data['Meridional Winds'], alpha=0.6, color='purple')
plt.title('Zonal Winds vs Meridional Winds', fontsize=16)
plt.xlabel('Zonal Winds (m/s)', fontsize=14)
plt.ylabel('Meridional Winds (m/s)', fontsize=14)
plt.grid(True)
plt.show()

# Scatterplot: Humidity vs Air Temperature
plt.figure(figsize=(10, 6))
sns.scatterplot(x=data['Humidity'], y=data['Air Temp'], alpha=0.6, color='orange')
plt.title('Humidity vs Air Temperature', fontsize=16)
plt.xlabel('Humidity (%)', fontsize=14)
plt.ylabel('Air Temperature (°C)', fontsize=14)
plt.grid(True)
plt.show()

# Geographic Distribution
plt.figure(figsize=(12, 8))
plt.scatter(data['Longitude'], data['Latitude'], c=data['Sea Surface Temp'], cmap='coolwarm', alpha=0.7)
plt.colorbar(label='Sea Surface Temperature (°C)')
plt.title('Geographic Distribution of Sea Surface Temperature', fontsize=16)
plt.xlabel('Longitude', fontsize=14)
plt.ylabel('Latitude', fontsize=14)
plt.grid(True)
plt.show()

"""FNN"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import matplotlib.pyplot as plt

# Convert categorical columns if needed (e.g., Year, Month, Day)
# For simplicity, we will not one-hot encode them but treat them as numerical inputs.
data['Date'] = pd.to_datetime(data['Date'])  # Ensure Date is in datetime format

# Define features (X) and target variable (y)
X = data[['Latitude', 'Longitude', 'Zonal Winds', 'Meridional Winds', 'Air Temp']]  # Input features
y = data['Sea Surface Temp']  # Target variable

for column in X.columns:
    if X[column].dtype == 'object':  # Check for object type (strings or non-numeric)
        print(f"Column '{column}' contains non-numeric values.")
        print(X[column].unique())

# Replace non-numeric characters (e.g., '.') with NaN
X.replace('.', np.nan, inplace=True)

# Convert to numeric (forcing errors to NaN)
X = X.apply(pd.to_numeric, errors='coerce')

# Fill missing values (NaNs) with column means
X = X.fillna(X.mean())

print(X.dtypes)

# Fill missing values with column mean
data = data.fillna(data.mean())

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),  # First hidden layer
    Dropout(0.3),  # Dropout for regularization
    Dense(32, activation='relu'),  # Second hidden layer
    Dropout(0.2),
    Dense(1, activation='linear')  # Output layer (for regression)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

print(y_train.dtypes)
print(y_test.dtypes)

y_train = pd.to_numeric(y_train, errors='coerce')
y_test = pd.to_numeric(y_test, errors='coerce')

# Replace NaN values in X_train and y_train
X_train = pd.DataFrame(X_train).fillna(X_train.mean())
y_train = pd.DataFrame(y_train).fillna(y_train.mean())

history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1000, batch_size=32, verbose=1)

y_pred = model.predict(X_test)

# Plot actual vs predicted values
import matplotlib.pyplot as plt

plt.scatter(y_test, y_pred)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Actual vs Predicted')
plt.show()

from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")
print(f"R^2 Score: {r2}")

import shap

explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)

shap.summary_plot(shap_values, X_test)