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

# == QUERIES ==
class Query(graphene.ObjectType ):
    """Query for Get Data"""

    all_products = graphene.List(Product)

    product = graphene.Field(Product, id=graphene.String(required=True))

    products_by_category = graphene.List(Product, category=graphene.String(required=True))

    all_orders = graphene.List(Order)

    search_products = graphene.List(
        Product,
        keyword=graphene.String(required=True),
        min_price=graphene.Int(),
        max_price=graphene.Int()
    )

    def resolve_all_products(self, info):
        return products_db

    def resolve_product(self, info, id):
        for product in products_db:
            if product["id"] == id:
                return product
        return None

    def resolve_product_by_category(self, info, category):
        return [p for p in products_db if p["category"].lower() == category.lower()]

    def resolve_all_orders(self, info):
        return orders_db

    def resolve_search_products(self, info, keyword, min_price=None, max_price=None):
        result = []
        for product in products_db:
            if keyword.lower() in product["name"].lower() or \
            keyword.lower() in product["description"].lower():

                if min_price and product["price"] < min_price: 
                    continue
                if max_price and product["price"] >  max_price: 
                    continue
                result.append(product)
        return result

# == MUTATIONS ==
class CreateOrder(graphene.Mutation):
    """Mutation for create order"""
    class Arguments:
        product_id = graphene.String(required=True)
        quantity= graphene.String(required=True)
        customer_name= graphene.String(required=True)
    
    order = graphene.Field(Order)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, product_id, quantity, customer_name):
        global order_counter

        product = None
        for p in products_db:
            if p["id"] == product_id:
                product = p
                break
        
        if not product:
            return CreateOrder(order=None, success=False, message="Product not found")
        
        if product["stock"] < quantity: 
            return CreateOrder(
                order=None,
                success=False,
                message=f"Insufficient stock. Available: {product['stock']}"
            )
        
        new_order = {
            "id": str(order_counter),
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "total_price": product["price"] * quantity,
            "customer_name": customer_name,
            "status": "PENDING",
            "created_at": datetime.now().isoformat()
        }

        product["stock"] -= quantity

        orders_db.append(new_order)
        order_counter += 1

        return CreateOrder(
            order=new_order,
            success=True,
            message="Order created successfully"
        )

class UpdateProductStock(graphene.Mutation):
    """Mutation for update stock product"""
    class Arguments:
        product_id = graphene.String(required=True)
        new_stock = graphene.Int(required=True)
    
    product = graphene.Field(Product)
    success = graphene.Boolean()
    message= graphene.String()

    def mutate(self, info, product_id, new_stock):
        for product in products_db:
            if product["id"] == product_id:
                product["stock"] == new_stock
                return UpdateProductStock(
                    product=product,
                    success=True,
                    message="Stock updated successfully"
                )
        
        return UpdateProductStock(
            product=None,
            success=False,
            message="Product not found"
        )




