import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib
import time

print("--- Traffic Speed Prediction Model Training ---")

# Load simulated traffic data
start_time = time.time()
print("Loading simulated_traffic.csv...")
df = pd.read_csv("simulated_traffic.csv")
print(f"Loaded {len(df)} records in {time.time() - start_time:.2f} seconds.")

# Feature Engineering
print("Performing feature engineering...")
# Encode hour as integer
df["hour_int"] = df["hour"].apply(lambda h: int(h.split(":")[0]))

# Encode road segments as categorical variables
segment_encoder = LabelEncoder()
df["segment_encoded"] = segment_encoder.fit_transform(df["segment_id"])
print("Feature engineering complete.")

# Prepare features and target
X = df[["segment_encoded", "hour_int"]]
y = df["speed_kph"]
print(f"Features shape: {X.shape}, Target shape: {y.shape}")

# Train-test split
print("Splitting data into training and testing sets (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")

# Train model
print("Training RandomForestRegressor model (n_estimators=100). This may take a few minutes...")
model_train_start_time = time.time()
# Using n_jobs=-1 to use all available cores for faster training, if appropriate for the dataset size
# For very large datasets, this can consume a lot of memory. n_estimators=100 is relatively small.
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=20, min_samples_split=10, min_samples_leaf=5)
model.fit(X_train, y_train)
print(f"Model training completed in {time.time() - model_train_start_time:.2f} seconds.")

# Evaluate
print("Evaluating model on the test set...")
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"✅ Mean Absolute Error (MAE): {mae:.2f} km/h")

# Save model and encoder for later use
model_filename = "traffic_speed_model.pkl"
encoder_filename = "segment_encoder.pkl"

print(f"Saving model to {model_filename}...")
joblib.dump(model, model_filename)
print(f"Saving segment encoder to {encoder_filename}...")
joblib.dump(segment_encoder, encoder_filename)
print("✅ Model and encoder saved successfully.")
print("--- Script finished ---")
