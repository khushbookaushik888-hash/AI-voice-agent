"""Edge Case Handlers for Robust Government Service Experience"""
from mock_data import PRODUCTS, CART
import random

async def handle_out_of_stock(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Handle out of stock scenarios with alternatives"""
    sku = arguments.get("sku", "")
    
    if sku not in PRODUCTS:
        await result_callback("Product not found.")
        return
    
    product = PRODUCTS[sku]
    
    # Simulate out of stock
    if random.choice([True, False]):
        # Find alternative in same category
        alternatives = [s for s, p in PRODUCTS.items() 
                       if p["category"] == product["category"] and s != sku]
        
        if alternatives:
            alt_sku = alternatives[0]
            alt_product = PRODUCTS[alt_sku]
            await result_callback(
                f"Sorry, {product['name']} is currently out of stock. "
                f"However, we have {alt_product['name']} (₹{alt_product['price']}) available. "
                f"Would you like to see this instead?"
            )
        else:
            await result_callback(
                f"{product['name']} is out of stock. "
                f"We can notify you when it's back in stock. Would you like that?"
            )
    else:
        await result_callback(f"{product['name']} is in stock!")


async def handle_payment_retry(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Handle payment failures with retry logic"""
    amount = arguments.get("amount", 0)
    method = arguments.get("method", "card")
    retry_count = arguments.get("retry_count", 0)
    
    if retry_count >= 2:
        await result_callback(
            "Payment failed multiple times. Please try a different payment method "
            "or contact your bank. You can also complete this purchase later."
        )
        return
    
    # Simulate payment with failure rate
    success = random.choice([True, True, False])
    
    if success:
        order_id = f"ORD{random.randint(10000, 99999)}"
        await result_callback(f"Payment successful! Order ID: {order_id}")
    else:
        await result_callback(
            f"Payment failed. This could be due to insufficient funds or network issues. "
            f"Would you like to try again or use a different payment method?"
        )


async def modify_order(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Modify existing order before shipment"""
    order_id = arguments.get("order_id", "")
    action = arguments.get("action", "")  # add_item, remove_item, change_address
    
    # Simulate order modification
    if action == "add_item":
        await result_callback(
            f"I've added the item to order {order_id}. "
            f"Updated total will be charged to your payment method."
        )
    elif action == "remove_item":
        await result_callback(
            f"Item removed from order {order_id}. "
            f"Refund will be processed within 3-5 business days."
        )
    elif action == "change_address":
        await result_callback(
            f"Delivery address updated for order {order_id}. "
            f"New estimated delivery: 3-5 days."
        )
    else:
        await result_callback(
            f"Order {order_id} can be modified. What would you like to change?"
        )


async def handle_price_objection(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Handle price objections with offers"""
    sku = arguments.get("sku", "")
    
    if sku not in PRODUCTS:
        await result_callback("Product not found.")
        return
    
    product = PRODUCTS[sku]
    
    # Offer solutions
    responses = [
        f"I understand. {product['name']} is priced at ₹{product['price']}. "
        f"We have a SAVE20 coupon that gives 20% off on purchases above ₹2000. "
        f"Would you like to add more items to qualify?",
        
        f"The price reflects premium quality. However, as a valued customer, "
        f"I can check if you have loyalty points to offset the cost. "
        f"Let me check your account.",
        
        f"I can show you similar items in a lower price range. "
        f"What's your budget?"
    ]
    
    await result_callback(random.choice(responses))


async def bundle_recommendation(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Recommend product bundles for better value"""
    category = arguments.get("category", "")
    
    bundles = {
        "Tops": "Pair with our Bottoms collection and get 15% off on the combo!",
        "Bottoms": "Complete the look with our Tops and Accessories - save ₹500 on bundle!",
        "Footwear": "Add matching accessories and get free shipping!",
        "Dresses": "Pair with our Accessories collection for a complete look - 10% off!"
    }
    
    response = bundles.get(category, "Check out our combo offers for great savings!")
    await result_callback(response)


async def notify_back_in_stock(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Register for back-in-stock notifications"""
    sku = arguments.get("sku", "")
    email = arguments.get("email", "")
    phone = arguments.get("phone", "")
    
    if sku not in PRODUCTS:
        await result_callback("Product not found.")
        return
    
    product = PRODUCTS[sku]
    await result_callback(
        f"You'll be notified when {product['name']} is back in stock. "
        f"We'll send updates via email and SMS."
    )


async def gift_wrap_service(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Add gift wrapping service"""
    order_id = arguments.get("order_id", "")
    message = arguments.get("message", "")
    
    await result_callback(
        f"Gift wrapping added to order {order_id} for ₹99. "
        f"Your personalized message will be included. "
        f"Perfect for gifting!"
    )


async def size_fit_guide(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Provide size and fit guidance"""
    sku = arguments.get("sku", "")
    
    if sku not in PRODUCTS:
        await result_callback("Product not found.")
        return
    
    product = PRODUCTS[sku]
    category = product["category"]
    
    guides = {
        "Tops": "For shirts, measure chest circumference. S(36-38), M(39-41), L(42-44), XL(45-47)",
        "Bottoms": "For jeans, measure waist. 28-30(S), 31-33(M), 34-36(L), 37-39(XL)",
        "Footwear": "Measure foot length. UK 6-7(S), 8-9(M), 10-11(L)",
        "Dresses": "Measure bust and waist. S(32-34), M(36-38), L(40-42)"
    }
    
    guide = guides.get(category, "Check product description for size chart")
    await result_callback(f"{product['name']} sizing: {guide}")


async def store_locator(function_name, tool_call_id, arguments, llm, context, result_callback):
    """Find nearest store location"""
    city = arguments.get("city", "")
    
    stores = {
        "Mumbai": "Store at Phoenix Mall, Lower Parel. Open 10 AM - 10 PM",
        "Delhi": "Store at Select City Walk, Saket. Open 10 AM - 10 PM",
        "Bangalore": "Store at UB City, Vittal Mallya Road. Open 10 AM - 10 PM"
    }
    
    store_info = stores.get(city, "We have stores in Mumbai, Delhi, and Bangalore")
    await result_callback(f"{store_info}. Would you like to reserve items for in-store pickup?")
