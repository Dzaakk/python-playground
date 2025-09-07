from flask import Flask, request, jsonify
import graphene
from graphene import Schema
from datetime import datetime
import json

# ===== DATA MODELS =====
products_db = [
    {
        "id": "1",
        "name": "Laptop Gaming ASUS ROG",
        "price": 15000000,
        "stock": 5,
        "category": "Electronics",
        "description": "High-end gaming laptop with RTX 4060",
    },
    {
        "id": "2",
        "name": "iPhone 15 Pro",
        "price": 20000000,
        "stock": 10,
        "category": "Electronics",
        "description": "Latest iPhone with chip A17 Pro",
    },
    {
        "id": "3",
        "name": "Nike Air Jordan 1",
        "price": 2500000,
        "stock": 3,
        "category": "Fashion",
        "description": "Limited edition sneakers",
    },
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
class Query(graphene.ObjectType):
    """Query for Get Data"""

    # Get all products
    all_products = graphene.List(Product)

    # Get product by ID
    product = graphene.Field(Product, id=graphene.String(required=True))

    # Get products by category
    products_by_category = graphene.List(
        Product, category=graphene.String(required=True)
    )

    # Get all orders
    all_orders = graphene.List(Order)

    # Search products
    search_products = graphene.List(
        Product,
        keyword=graphene.String(required=True),
        min_price=graphene.Int(),
        max_price=graphene.Int(),
    )

    def resolve_all_products(self, info):
        return products_db

    def resolve_product(self, info, id):
        for product in products_db:
            if product["id"] == id:
                return product
        return None

    def resolve_products_by_category(self, info, category):
        return [p for p in products_db if p["category"].lower() == category.lower()]

    def resolve_all_orders(self, info):
        return orders_db

    def resolve_search_products(self, info, keyword, min_price=None, max_price=None):
        results = []
        for product in products_db:
            # Search by keyword in name or description
            if (
                keyword.lower() in product["name"].lower()
                or keyword.lower() in product["description"].lower()
            ):
                # Filter by price range if provided
                if min_price and product["price"] < min_price:
                    continue
                if max_price and product["price"] > max_price:
                    continue
                results.append(product)
        return results


# == MUTATIONS ==
class CreateOrder(graphene.Mutation):
    """Mutation for create order"""

    class Arguments:
        product_id = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        customer_name = graphene.String(required=True)

    # Return type
    order = graphene.Field(Order)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, product_id, quantity, customer_name):
        global order_counter

        # Find product
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
                message=f"Insufficient stock. Available: {product['stock']}",
            )

        # Create order
        new_order = {
            "id": str(order_counter),
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "total_price": product["price"] * quantity,
            "customer_name": customer_name,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
        }

        # Update stock
        product["stock"] -= quantity

        # Save order
        orders_db.append(new_order)
        order_counter += 1

        return CreateOrder(
            order=new_order, success=True, message="Order created successfully"
        )


class UpdateProductStock(graphene.Mutation):
    """Mutation for update stock product"""

    class Arguments:
        product_id = graphene.String(required=True)
        new_stock = graphene.Int(required=True)

    product = graphene.Field(Product)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, product_id, new_stock):
        for product in products_db:
            if product["id"] == product_id:
                product["stock"] = new_stock
                return UpdateProductStock(
                    product=product, success=True, message="Stock updated successfully"
                )

        return UpdateProductStock(
            product=None, success=False, message="Product not found"
        )


class AddProduct(graphene.Mutation):
    """Mutation for add new product"""

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Int(required=True)
        stock = graphene.Int(required=True)
        category = graphene.String(required=True)
        description = graphene.String()

    product = graphene.Field(Product)
    success = graphene.Boolean()

    def mutate(self, info, name, price, stock, category, description=""):
        new_product = {
            "id": str(len(products_db) + 1),
            "name": name,
            "price": price,
            "stock": stock,
            "category": category,
            "description": description,
        }
        products_db.append(new_product)

        return AddProduct(product=new_product, success=True)


class Mutation(graphene.ObjectType):
    """Root Mutation"""

    create_order = CreateOrder.Field()
    update_product_stock = UpdateProductStock.Field()
    add_product = AddProduct.Field()


# ===== FLASK APP SETUP =====
app = Flask(__name__)
app.debug = True

# Create GraphQL schema
schema = graphene.Schema(query=Query, mutation=Mutation)


# Custom GraphQL endpoint handler
@app.route("/graphql", methods=["GET", "POST", "OPTIONS"])
def graphql_server():
    if request.method == "OPTIONS":
        # Handle CORS preflight
        response = jsonify({"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    # Get query from request
    if request.method == "GET":
        query = request.args.get("query")
        variables = request.args.get("variables")
    else:
        data = request.get_json()
        query = data.get("query") if data else None
        variables = data.get("variables") if data else None

    if not query:
        # Return GraphiQL interface for GET requests without query
        if request.method == "GET":
            return GRAPHIQL_HTML, 200, {"Content-Type": "text/html"}
        return jsonify({"error": "No query provided"}), 400

    # Parse variables if string
    if variables and isinstance(variables, str):
        try:
            variables = json.loads(variables)
        except:
            variables = None

    # Execute query
    try:
        result = schema.execute(query, variable_values=variables)

        response_data = {"data": result.data}

        if result.errors:
            response_data["errors"] = [str(error) for error in result.errors]

        response = jsonify(response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GraphiQL HTML interface
GRAPHIQL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GraphiQL</title>
    <link href="https://unpkg.com/graphiql@2.4.7/graphiql.min.css" rel="stylesheet" />
    <style>
        body { height: 100vh; margin: 0; }
        #graphiql { height: 100%; }
    </style>
</head>
<body>
    <div id="graphiql">Loading...</div>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/graphiql@2.4.7/graphiql.min.js"></script>
    <script>
        const fetcher = GraphiQL.createFetcher({
            url: '/graphql',
        });
        
        const root = ReactDOM.createRoot(document.getElementById('graphiql'));
        root.render(
            React.createElement(GraphiQL, {
                fetcher: fetcher,
                defaultQuery: `# Welcome to GraphiQL
#
# Try this query:
{
  allProducts {
    id
    name
    price
    stock
  }
}`,
            })
        );
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return """
    <h1>GraphQL E-Commerce API</h1>
    <p>Access GraphQL Playground at: <a href="/graphql">/graphql</a></p>
    <h3>Available Queries:</h3>
    <ul>
        <li>allProducts - Get all products</li>
        <li>product(id) - Get product by ID</li>
        <li>productsByCategory(category) - Get products by category</li>
        <li>searchProducts(keyword, minPrice, maxPrice) - Search products</li>
        <li>allOrders - Get all orders</li>
    </ul>
    <h3>Available Mutations:</h3>
    <ul>
        <li>createOrder - Create new order</li>
        <li>updateProductStock - Update product stock</li>
        <li>addProduct - Add new product</li>
    </ul>
    """


if __name__ == "__main__":
    print("GraphQL Server running at http://localhost:5000/graphql")
    print("GraphiQL interface available at http://localhost:5000/graphql")
    app.run(port=5000)
