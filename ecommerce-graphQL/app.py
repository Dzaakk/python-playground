from flask import Flask
from flask_graphql import GraphQLView
import graphene
from datetime import datetime

# == Data Models ==
products_db = [
 {
        "id": "1",
        "name": "Laptop Gaming ASUS ROG",
        "price": 15000000,
        "stock": 5,
        "category": "Electronics",
        "description": "High-end gaming laptop with RTX 4060"
    },
    {
        "id": "2", 
        "name": "iPhone 15 Pro",
        "price": 20000000,
        "stock": 10,
        "category": "Electronics",
        "description": "Latest iPhone with chip A17 Pro"
    },
    {
        "id": "3",
        "name": "Nike Air Jordan 1",
        "price": 2500000,
        "stock": 3,
        "category": "Fashion",
        "description": "Limited edition sneakers"
    }
]

orders_db = []
order_counter = 1


# == GRAPHQL Types ==
class Product(graphene.ObjectType):
    """Type for Product"""
    id = graphene.ID()
    name = graphene.String()
    price = graphene.Int()
    stock = graphene.Int()
    category = graphene.String()
    description = graphene.String()
    
class Order(graphene.ObjectType):
    """Type for Order"""
    id = graphene.ID()
    product_id = graphene.String()
    product_name = graphene.String()
    quantity = graphene.Int()
    total_price = graphene.Int()
    customer_name = graphene.String()
    status = graphene.String()
    created_at = graphene.String()

