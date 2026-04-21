from app import create_app
import qrcode

print("MODULE:", qrcode)
print("PATH:", qrcode.__file__)
print("HAS MAKE:", hasattr(qrcode, "make"))

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)