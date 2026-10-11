# Define la clase que representa el modelo de datos de un producto
class Product:
    # Inicializa el objeto producto
    def __init__(self, id, title, price, description, category, image):
        self.id = id
        self.title = title
        self.price = price
        self.description = description
        self.category = category
        self.image = image

    # Toma los datos de la API y los convierte en el objeto
    @classmethod
    def from_json(cls, data):
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            price=float(data.get("price", 0.0)),
            description=data.get("description", ""),
            category=data.get("category", ""),
            image=data.get("image", "")
        )