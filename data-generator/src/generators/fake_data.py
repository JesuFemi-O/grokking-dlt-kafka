import random
from datetime import datetime, timedelta
from typing import Dict, Any
from uuid import uuid4

from faker import Faker

from models import User, Product, Order, Payment, Return, Address
from .relationships import data_state

fake = Faker()


def generate_fake_user() -> User:
    """Generate a realistic user"""
    addresses = [
        Address(
            street=fake.street_address(),
            city=fake.city(),
            country=fake.country(),
            postal_code=fake.postcode() if random.choice([True, False]) else None,
        )
        for _ in range(random.randint(1, 3))
    ]
    
    return User(
        id=random.randint(1, 1_000_000),
        name=fake.name(),
        email=fake.email(),
        age=random.randint(18, 80),
        status=random.choice(["active", "inactive", "pending"]),
        addresses=addresses,
        created_at=fake.date_time(),
        is_verified=fake.boolean(),
    )


def generate_fake_product() -> Product:
    """Generate a realistic product"""
    return Product(
        product_id=random.randint(1, 10_000),
        name=fake.word().title() + " " + fake.word().title(),
        category=random.choice(["Electronics", "Clothing", "Books", "Home", "Sports"]),
        price=round(random.uniform(10.0, 500.0), 2),
        stock=random.randint(0, 500),
        created_at=fake.date_time(),
    )


def generate_fake_order() -> Order:
    """Generate a realistic order"""
    # Select random products (1-5 items)
    selected_products = random.sample(data_state.product_ids, random.randint(1, 5))
    
    # Calculate realistic total (product count * average price range)
    base_price_per_item = random.uniform(15.0, 200.0)
    total_amount = round(sum(base_price_per_item * random.uniform(0.8, 1.2) 
                            for _ in selected_products), 2)
    
    return Order(
        order_id=random.randint(10000, 99999),
        user_id=random.choice(data_state.user_ids),
        product_ids=selected_products,
        total_amount=total_amount,
        status=random.choices(
            ["pending", "processing", "completed", "cancelled"],
            weights=[10, 20, 60, 10]  # Most orders are completed
        )[0],
        created_at=fake.date_time_between(start_date='-30d', end_date='now')
    )


def generate_fake_payment() -> Payment:
    """Generate a payment tied to an existing order"""
    # 70% chance to use an existing order, 30% chance for new order ID
    if data_state.generated_orders and random.random() < 0.7:
        related_order = random.choice(data_state.generated_orders)
        order_id = str(related_order['order_id'])
        amount = related_order['total_amount']
        # Payment date should be after order date
        min_date = related_order['created_at']
        if isinstance(min_date, int):
            min_date = datetime.fromtimestamp(min_date / 1000)
        created_at = fake.date_time_between(
            start_date=min_date, 
            end_date=min_date + timedelta(days=7)
        )
    else:
        order_id = str(random.randint(10000, 99999))
        amount = round(random.uniform(50.0, 1000.0), 2)
        created_at = fake.date_time_between(start_date='-30d', end_date='now')
    
    # Payment success rate: 85%
    successful = random.choices([True, False], weights=[85, 15])[0]
    
    return Payment(
        payment_id=str(uuid4()),
        order_id=order_id,
        amount=amount,
        method=random.choices(
            ["credit_card", "paypal", "bank_transfer", "apple_pay", "google_pay"],
            weights=[40, 25, 15, 10, 10]
        )[0],
        successful=successful,
        processed_at=created_at
    )


def generate_fake_return() -> Return:
    """Generate a return tied to an existing completed order"""
    # 80% chance to use an existing order, 20% chance for random order ID
    completed_orders = data_state.get_completed_orders()
    
    if completed_orders and random.random() < 0.8:
        related_order = random.choice(completed_orders)
        order_id = str(related_order['order_id'])
        
        # Return date should be after order date but within reasonable timeframe
        min_date = related_order['created_at']
        if isinstance(min_date, int):
            min_date = datetime.fromtimestamp(min_date / 1000)
        
        # Returns typically happen within 30 days
        max_return_date = min(
            min_date + timedelta(days=30),
            datetime.now()
        )
        
        created_at = fake.date_time_between(start_date=min_date, end_date=max_return_date)
        
        # Return some or all products from the order
        products_to_return = random.sample(
            related_order['product_ids'],
            random.randint(1, len(related_order['product_ids']))
        )
        
        # Refund amount is proportional to returned products
        refund_ratio = len(products_to_return) / len(related_order['product_ids'])
        refund_amount = round(related_order['total_amount'] * refund_ratio, 2)
    else:
        # Fallback to random data
        order_id = str(random.randint(10000, 99999))
        products_to_return = random.sample(data_state.product_ids, random.randint(1, 3))
        refund_amount = round(random.uniform(25.0, 500.0), 2)
        created_at = fake.date_time_between(start_date='-30d', end_date='now')
    
    return Return(
        return_id=str(uuid4()),
        order_id=order_id,
        product_ids=products_to_return,
        reason=random.choice([
            "defective", "wrong_item", "not_as_described", 
            "changed_mind", "damaged_in_shipping", "size_issue"
        ]),
        status=random.choices(
            ["requested", "approved", "processing", "completed", "rejected"],
            weights=[15, 20, 25, 35, 5]
        )[0],
        refund_amount=refund_amount,
        requested_at=created_at
    )