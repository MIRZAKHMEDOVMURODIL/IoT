import pandas as pd
from scipy.stats import pearsonr
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


df = pd.read_csv(r'.csv') 


# Correlation Analysis
correlations = {}
for column in df.columns[:-1]:  # Exclude CPK column itself
    corr, _ = pearsonr(df[column], df['CPK'])
    correlations[column] = corr

# Print correlations
print("Correlation coefficients with CPK:")
for var, corr in correlations.items():
    print(f"{var}: {corr:.2f}")

# Regression Analysis
X = df[['  ', '  ']]  # Features
y = df['CPK']  # Target variable


X = sm.add_constant(X)
model = sm.OLS(y, X).fit()

print("\nRegression Summary:")
print(model.summary())


model_sklearn = LinearRegression()
model_sklearn.fit(X[['const', 'Variable1', 'Variable2']], y)

# Print coefficients and intercept
print("\nCoefficients (scikit-learn):")
print("Intercept:", model_sklearn.intercept_)
print("Coefficients:", model_sklearn.coef_)

# Predict CPK values
y_pred = model_sklearn.predict(X[['const', 'Variable1', 'Variable2']])

# Evaluate model performance (optional)
print("\nModel Evaluation (scikit-learn):")
print("Mean Squared Error:", mean_squared_error(y, y_pred))
print("R-squared:", r2_score(y, y_pred))
