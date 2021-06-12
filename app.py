import random
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():

    x = open('prefix.txt', 'r')
    y = open('first.txt', 'r')
    z = open('second.txt', 'r')

    a = []
    b = []
    c = []

    for line in x:
      a.append(line)

    for line in y:
      b.append(line)

    for line in z:
      c.append(line)

    d = str(random.choice(a))
    # d = d[:-2]
    d += ' '
    e = str(random.choice(b))
    # e = e[:-2]
    if not e.endswith('-'):
      e += ' '
    f = str(random.choice(c))
    # f = f[:-2]

    result = d + e + f

    x.close()
    y.close()
    z.close()
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()
