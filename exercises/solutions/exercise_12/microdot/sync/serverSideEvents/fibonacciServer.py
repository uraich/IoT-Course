from microdot.microdot import Microdot
from wifi_connect import connect, getIPAddress
from time import sleep

connect()
app = Microdot()

@app.get('/fibonacci')
def fibonacci(request):
    def generate_fibonacci():
        a, b = 0, 1
        while a < 100:
            yield str(a) + '\n'
            a, b = b, a + b
            sleep(1)

    return generate_fibonacci()


app.run(debug=True,host=getIPAddress(),port=80)
