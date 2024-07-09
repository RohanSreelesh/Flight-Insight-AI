import pandas as pd
import numpy as np
from datetime import datetime
import os

def clean_airline_reviews(file_path : str):
    # Read the CSV file
    dataFrame = pd.read_csv(file_path)

    # Function to convert rating to numeric
    def convert_rating(rating):
        try:
            return int(rating)
        except ValueError:
            return np.nan

    # Clean and transform columns
    dataFrame['overall_rating'] = dataFrame['overall_rating'].apply(convert_rating)
    dataFrame['verification'] = dataFrame['verification'].replace('✅ Trip Verified', 'Verified').replace('Not Verified', 'Not Verified')
    
    # Convert date to datetime
    dataFrame['Date Flown'] = pd.to_datetime(dataFrame['Date Flown'], format='%B %Y', errors='coerce')
    
    # Convert numeric columns to appropriate types
    numeric_columns = ['Seat Comfort', 'Cabin Staff Service', 'Food & Beverages', 'Inflight Entertainment', 'Ground Service', 'Wifi & Connectivity', 'Value For Money']
    for col in numeric_columns:
        dataFrame[col] = pd.to_numeric(dataFrame[col], errors='coerce')

    # Clean up 'Recommended' column
    dataFrame['Recommended'] = dataFrame['Recommended'].map({'yes': True, 'no': False})

    # Handle missing values
    categorical_columns = ['Aircraft', 'Type Of Traveller', 'Seat Type', 'Route']
    for col in categorical_columns:
        dataFrame[col] = dataFrame[col].fillna('Not specified')

    # Remove rows only if critical information is missing
    dataFrame = dataFrame.dropna(subset=['airline', 'review_text'])

    # For numeric ratings, replace NaN with the mean of that column
    for col in numeric_columns + ['overall_rating']:
        dataFrame[col] = dataFrame[col].fillna(dataFrame[col].mean())

    # Clean the review text
    dataFrame['review_text'] = dataFrame['review_text'].apply(lambda x: str(x).strip() if pd.notnull(x) else '')

    # Reset the index
    dataFrame = dataFrame.reset_index(drop=True)

    return dataFrame

def process_folder(folder_path: str):
    # Get all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    all_data = []

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        print(f"Processing {file}...")

        # Clean the data
        cleaned_df = clean_airline_reviews(file_path)
        all_data.append(cleaned_df)

        # Display some statistics 
        print(f"\nCleaned Data Statistics for {file}:")
        print(f"Total number of reviews: {len(cleaned_df)}")
        print(f"Average rating: {cleaned_df['overall_rating'].mean():.2f}")
        print(f"Number of verified reviews: {cleaned_df['verification'].value_counts().get('Verified', 0)}")
        print(f"Number of routes: {cleaned_df['Route'].nunique()}")

    # Combine all cleaned data into one DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)

    # Save the cleaned data
    combined_file_path = os.path.join(folder_path, "all_airlines_reviews_cleaned.csv")
    combined_df.to_csv(combined_file_path, index=False)

    print(f"Combined cleaned data saved to 'all_airlines_reviews_cleaned.csv'")
    print(f"Total number of reviews across all airlines: {len(combined_df)}")

folder_path = './Data'
if __name__ == "__main__":
    process_folder(folder_path)
    print("All CSV files in the folder have been processed and combined.")