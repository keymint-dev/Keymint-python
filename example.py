"""
Example usage of the KeyMint Python SDK

Before running this example:
1. Get your API key from: https://app.keymint.dev
2. Get your product ID from your KeyMint dashboard
3. Set environment variables:
   export KEYMINT_API_KEY="your_token_here"
   export KEYMINT_PRODUCT_ID="your_product_id_here"
"""

import os
import uuid
from keymint import KeyMint, KeyMintApiError

def main():
    # Get credentials from environment variables
    api_key = os.environ.get('KEYMINT_API_KEY')
    product_id = os.environ.get('KEYMINT_PRODUCT_ID')
    
    if not api_key:
        print("❌ Please set KEYMINT_API_KEY environment variable")
        return
    
    if not product_id:
        print("❌ Please set KEYMINT_PRODUCT_ID environment variable")
        return
    
    print("🚀 KeyMint Python SDK Example")
    print("-" * 40)
    
    # Initialize the SDK
    sdk = KeyMint(api_key)
    
    try:
        # 1. Create a customer
        print("1. Creating a customer...")
        customer_response = sdk.create_customer({
            'name': f'Example Customer {uuid.uuid4().hex[:8]}',
            'email': f'example-{uuid.uuid4().hex[:8]}@example.com'
        })
        customer_id = customer_response['data']['id']
        print(f"   ✅ Customer created: {customer_id}")
        
        # 2. Create a license key for the customer
        print("2. Creating license key...")
        license_response = sdk.create_key({
            'productId': product_id,
            'maxActivations': '3',
            'customerId': customer_id
        })
        license_key = license_response['key']
        print(f"   ✅ License key created: {license_key}")
        
        # 3. Get license key details
        print("3. Getting license key details...")
        key_details = sdk.get_key({
            'productId': product_id,
            'licenseKey': license_key
        })
        license_info = key_details['data']['license']
        print(f"   ✅ Max activations: {license_info['maxActivations']}")
        print(f"   ✅ Current activations: {license_info['activations']}")
        
        # 4. Activate the license
        print("4. Activating license...")
        activate_response = sdk.activate_key({
            'productId': product_id,
            'licenseKey': license_key,
            'hostId': f'example-device-{uuid.uuid4().hex[:8]}',
            'deviceTag': 'Example Device'
        })
        print(f"   ✅ License activated: {activate_response['message']}")
        
        # 5. Check updated activation count
        print("5. Checking updated activations...")
        updated_details = sdk.get_key({
            'productId': product_id,
            'licenseKey': license_key
        })
        updated_activations = updated_details['data']['license']['activations']
        print(f"   ✅ Updated activations: {updated_activations}")
        
        # 6. Get customer's license keys
        print("6. Getting customer with license keys...")
        customer_with_keys = sdk.get_customer_with_keys({
            'customerId': customer_id
        })
        print(f"   ✅ Retrieved customer with {len(customer_with_keys['data'].get('keys', []))} keys")
        
        # 7. Clean up - delete the customer
        print("7. Cleaning up...")
        sdk.delete_customer({'customerId': customer_id})
        print("   ✅ Customer deleted")
        
        print("\n🎉 Example completed successfully!")
        
    except KeyMintApiError as e:
        print(f"\n❌ KeyMint API Error:")
        print(f"   Message: {e.message}")
        print(f"   Code: {e.code}")
        print(f"   Status: {e.status}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
