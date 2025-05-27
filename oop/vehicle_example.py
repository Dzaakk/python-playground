class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        self._speed = 0
    
    def start_engine(self):
        print(f"{self.brand} {self.model} engine started.")

    def accelerate(self, increment):
        self._speed += increment
        print(f"{self.brand} is now going at {self._speed} km/h")
    
    def stop(self):
        self._speed = 0
        print(f"{self.brand} has stopped.")
        
    def get_speed(self):
        return self._speed
    
class Car(Vehicle):
    def __init__(self, brand, model, fuel_type):
        super().__init__(brand, model)
        self.fuel_type = fuel_type
    
    def show_info(self):
        print(f"Car: {self.brand} {self.model}, Fuel: {self.fuel_type}")

if __name__ == "__main__":
    car1 = Car("Toyota", "Camry", "Petrol")
    car1.show_info()
    car1.start_engine()
    car1.accelerate(30)
    car1.accelerate(20)
    print("Current speed:", car1.get_speed())
    car1.stop()
