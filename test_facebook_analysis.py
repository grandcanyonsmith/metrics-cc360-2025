#!/usr/bin/env python3
"""
Test script to run Facebook subscription analysis query
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import the connection function
from app import get_snowflake_connection

# Import the query functions
from queries.facebook_subscription_analysis import (
    facebook_subscription_analysis_query,
    facebook_subscription_summary_query
)

def main():
    """Run the Facebook subscription analysis"""
    try:
        print("🔍 Running Facebook Subscription Analysis...")
        print("=" * 60)
        
        # Get database connection
        conn = get_snowflake_connection()
        
        # Run summary query first
        print("\n📊 SUMMARY STATISTICS:")
        print("-" * 30)
        summary_query = facebook_subscription_summary_query()
        df_summary = pd.read_sql(summary_query, conn)
        
        if not df_summary.empty:
            summary = df_summary.iloc[0]
            print(f"Total Subscriptions (last 30 days): {summary['TOTAL_SUBSCRIPTIONS']}")
            print(f"From Facebook Lead Ads: {summary['FROM_FACEBOOK']}")
            print(f"From Other Sources: {summary['FROM_OTHER_SOURCES']}")
            print(f"Facebook Percentage: {summary['FACEBOOK_PERCENTAGE']}%")
        else:
            print("No summary data found")
        
        # Run detailed analysis
        print("\n📋 DETAILED SUBSCRIPTION DATA:")
        print("-" * 40)
        detailed_query = facebook_subscription_analysis_query()
        df_detailed = pd.read_sql(detailed_query, conn)
        
        if not df_detailed.empty:
            print(f"Found {len(df_detailed)} subscriptions")
            print("\nFirst 10 records:")
            print("-" * 40)
            
            # Display first 10 records
            for idx, row in df_detailed.head(10).iterrows():
                print(f"\n{idx + 1}. {row['CUSTOMER_NAME'] or 'N/A'}")
                print(f"   Email: {row['CUSTOMER_EMAIL']}")
                print(f"   Product: {row['PRODUCT_NAME']}")
                print(f"   Created: {row['CREATED']}")
                print(f"   Status: {row['STATUS']}")
                print(f"   From Facebook: {row['FROM_FACEBOOK']}")
                if row['FROM_FACEBOOK'] == 'Yes':
                    print(f"   Facebook Email: {row['FACEBOOK_EMAIL']}")
                    print(f"   Facebook Phone: {row['FACEBOOK_PHONE']}")
            
            # Show breakdown by product
            print("\n📈 BREAKDOWN BY PRODUCT:")
            print("-" * 30)
            product_breakdown = df_detailed.groupby(['PRODUCT_NAME', 'FROM_FACEBOOK']).size().unstack(fill_value=0)
            print(product_breakdown)
            
            # Show breakdown by attribution
            print("\n🎯 ATTRIBUTION BREAKDOWN:")
            print("-" * 30)
            attribution_breakdown = df_detailed['ATTRIBUTION_SOURCE'].value_counts()
            print(attribution_breakdown)
            
        else:
            print("No detailed data found")
        
        conn.close()
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 